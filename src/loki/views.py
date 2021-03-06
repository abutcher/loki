# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import time
import pickle

from copy import deepcopy

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test
from django.template import RequestContext

from loki.models import Host
from loki.models import Master, Slave, Builder
from loki.models import Config, ConfigParam
from loki.models import Status, StatusParam
from loki.models import Step, StepParam
from loki.models import Scheduler, SchedulerParam
from loki.models import status_content_type
from loki.models import step_content_type
from loki.models import scheduler_content_type

from loki.model_helpers import introspect_module
from loki.helpers import config_importer
from loki.helpers import type_sniffer
from loki.forms import BuilderForm


def home(request, master=None, builder=None):
    """
    Handles home, Master details and Builder details pages.
    """
    context = {}
    context['bots'] = sorted(Master.objects.all(), key=lambda bot: bot.name)
    context['steps'] = Config.objects.filter(content_type=step_content_type)
    context['status'] = Config.objects.filter(content_type=status_content_type)
    context['scheduler'] = Config.objects.filter(
        content_type=scheduler_content_type)
    if builder:
        render_template = 'builder'
        master = filter(lambda bot: bot.name == master, context['bots'])[0]
        builder = Builder.objects.get(name=builder, master=master)
        context['builder'] = builder
        context['master'] = builder.master
    elif master:
        render_template = 'master'
        master = filter(lambda bot: bot.name == master, context['bots'])[0]
        context['master'] = master
    else:
        render_template = 'home'
        context['hosts'] = Host.objects.exclude(id=1)
        context['builders'] = Builder.objects.order_by('name')
    return render_to_response('loki/%s.html' % render_template, context,
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def action(request, action, master, slave=None):
    """
    executes a passed action to a master/slave bot
    """
    masters = Master.objects.none()
    if slave:
        if slave == 'all':
            slaves = Slave.objects.all()
        else:
            slaves = Slave.objects.filter(name=slave)
            masters = [Master.objects.get(name=master)]
        for slave in slaves:
            slave.bot_run(action)
        time.sleep(1)
    elif master:
        if master == 'all':
            masters = Master.objects.all()
        else:
            masters = [Master.objects.get(name=master)]
        for master in masters:
            master.bot_run(action)
        time.sleep(1)

    if len(masters) == 1:
        return HttpResponseRedirect(reverse('loki.views.home',
                                    args=[master]))
    else:
        return home(request)


@user_passes_test(lambda u: u.is_superuser)
def config_add(request, type, bot_id, config_id):
    config = Config.objects.get(pk=config_id)
    config_num = 0
    if type == 'step':
        config_num = 1
        builder = Builder.objects.get(pk=bot_id)
        step_with_max_num = Step.objects.filter(
                builder=builder).order_by('-num')
        if step_with_max_num:
            config_num = step_with_max_num[0].num + 1
    context = {'type': type,
               'bot': bot_id,
               'config': config,
               'config_num': config_num, }

    return render_to_response('loki/ajax/config.html', context,
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def config_load(request, type, config_id):
    if type == 'step':
        config = Step.objects.get(pk=config_id)
    elif type == 'status':
        config = Status.objects.get(pk=config_id)
    elif type == 'scheduler':
        config = Scheduler.objects.get(pk=config_id)
    context = {type: config, }

    return render_to_response('loki/ajax/%s.html' % type, context,
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def config_step_save(request, bot_id):
    result = ''
    if request.method == 'POST':
        builder = Builder.objects.get(id=bot_id)
        data = request.POST.copy()
        # get a step or create a newone
        if 'stepid' in data and data['stepid']:
            step = Step.objects.get(id=data['stepid'])
            step.num = data['step_num']
            del data['stepid']
            del data['step_num']
        else:
            config = Config.objects.get(id=data['config_type_id'])
            step = Step(builder=builder, type=config, num=data['config_num'])
            step.save()
            del data['config_type_id']
            del data['config_num']

        params_2_add = []
        # add and upate params
        step_params = step.params.all()
        for p, v in data.items():
            v = type_sniffer(v)
            param_type = ConfigParam.objects.get(id=p)
            s = step.params.filter(type=param_type)
            if s:
                s = s[0]
                s.val = pickle.dumps(v)
                s.default = (v == param_type.loads_default())
                s.save()
            else:
                param = StepParam(step=step, type=param_type,
                                  val=pickle.dumps(v),
                                  default=(v == param_type.loads_default()))
                params_2_add.append(param)
        if params_2_add:
            step.params = params_2_add
        step.save()
        result = step.id
    return HttpResponse(result)


@user_passes_test(lambda u: u.is_superuser)
def config_status_save(request, bot_id):
    result = ''
    if request.method == 'POST':
        master = Master.objects.get(id=bot_id)
        data = request.POST.copy()
        # get a status or create a newone
        if 'configid' in data and data['configid']:
            status = Status.objects.get(id=data['configid'])
            del data['configid']
        else:
            config = Config.objects.get(id=data['config_type_id'])
            status = Status(master=master, type=config)
            status.save()
            del data['config_type_id']

        params_2_add = []
        # add and upate params
        status_params = status.params.all()
        for p, v in data.items():
            v = type_sniffer(v)
            param_type = ConfigParam.objects.get(id=p)
            s = status.params.filter(type=param_type)
            if s:
                s = s[0]
                s.val = pickle.dumps(v)
                s.default = (v == param_type.loads_default())
                s.save()
            else:
                param = StatusParam(status=status, type=param_type,
                                  val=pickle.dumps(v),
                                  default=(v == param_type.loads_default()))
                params_2_add.append(param)

        if params_2_add:
            status.params = params_2_add
        status.save()
        result = status.id

    return HttpResponse(result)


@user_passes_test(lambda u: u.is_superuser)
def config_scheduler_save(request, bot_id):
    result = ''
    if request.method == 'POST':
        master = Master.objects.get(id=bot_id)
        data = request.POST.copy()
        # get a scheduler or create a newone
        if 'configid' in data and data['configid']:
            scheduler = Scheduler.objects.get(id=data['configid'])
            del data['configid']
        else:
            config = Config.objects.get(id=data['config_type_id'])
            scheduler = Scheduler(master=master, type=config)
            scheduler.save()
            del data['config_type_id']

        params_2_add = []
        # update existing params
        for p in scheduler.params.all():
            #TODO: update existing params
            #      only to creating a new one
            #      so just passing for now
            # how: check if default, if changed, save it
            #      then delete the key from the dict
            #      so it's not reprocessed
            #      and add the param to the params 2 add
            pass
        # add new params
        for p, v in data.items():
            v = type_sniffer(v)
            param_type = ConfigParam.objects.get(id=p)
            if v != param_type.default:
                param = SchedulerParam(
                    scheduler=scheduler, type=param_type, val=pickle.dumps(v))
                params_2_add.append(param)
        scheduler.params = params_2_add
        scheduler.save()
        result = scheduler.id

    return HttpResponse(result)


@user_passes_test(lambda u: u.is_superuser)
def config_delete(request, type):
    result = ''
    if request.method == 'POST':
        data = request.POST
        if type == 'step':
            config = Step.objects.get(id=data['configid'])
        elif type == 'status':
            config = Status.objects.get(id=data['configid'])
        elif type == 'scheduler':
            config = Scheduler.objects.get(id=data['configid'])
        config.delete()
    return HttpResponse(result)


@user_passes_test(lambda u: u.is_superuser)
def import_config(request, type):
    # do import if we're importing
    if request.method == 'POST' and 'import' in request.POST:
        config_importer(request.POST['import'], type)

        if 'path' in request.POST:
            path = request.POST['path']
        else:
            path = None
        return HttpResponseRedirect('%s?path=%s' % (
            reverse('loki.views.import_config', args=[type]), path))

    # not importing so get configs in the db and configs from the path
    configs = [mod[0] for mod in Config.objects.values_list('module')]
    path = 'buildbot.%s' % type
    if request.method == 'GET' and 'path' in request.GET:
        path = request.GET['path']
    introspected = introspect_module(path=path)

    # calculate which introspected configs are already in the db
    del_classes = []
    for config in introspected:
        if introspected[config][0] in configs:
            del_classes.append(config)

    # remove the existing configs from the displayed list.
    for del_class in del_classes:
        del introspected[del_class]

    # render
    context = {'path': path,
                'type': type,
                'classes': introspected, }
    return render_to_response('loki/import.html', context,
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def log(request, master):
    """
    display a master's log
    """
    bots = Master.objects.all()
    master = bots.get(name=master)
    context = {'bots': bots,
               'master': master,
               'log': master.get_log(), }
    return render_to_response('loki/log.html', context,
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def clone(request, master, builder):
    """
    clone a builder
    """
    bots = Master.objects.all()
    builder = Builder.objects.get(name=builder, master=bots.get(name=master))
    new_builder = deepcopy(builder)
    new_builder.name = "NewBuilder"
    if request.method == 'POST':
        new_builder.id = None
        form = BuilderForm(request.POST, instance=new_builder)
        form.save()
        # no copy the steps
        for step in builder.steps.all():
            params = step.params.all()
            step = deepcopy(step)
            step.id = None
            step.builder = new_builder
            step.save()
            # include the steps params
            for param in params:
                param = deepcopy(param)
                param.id = None
                param.step = step
                param.save()
        return HttpResponseRedirect(reverse('loki.views.home',
                    args=[new_builder.master.name, new_builder.name]))
    else:
        form = BuilderForm(instance=new_builder)
    context = {'form': form,
               'bots': bots,
               'builder': builder, }
    return render_to_response('loki/clone.html', context,
                              context_instance=RequestContext(request))
