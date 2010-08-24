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
from loki.models import cfg_objs

from loki.model_helpers import introspect_module
from loki.helpers import config_importer
from loki.helpers import type_sniffer
from loki.forms import ConfigParamFormSet


def home(request, master=None, builder=None):
    """
    TODO: document me.
    """
    context = {}
    context['bots'] = Master.objects.all()
    context['steps'] = Config.objects.filter(content_type=step_content_type)
    context['status'] = Config.objects.filter(content_type=status_content_type)
    context['scheduler'] = Config.objects.filter(
        content_type=scheduler_content_type)
    render_template = 'home'
    if builder:
        render_template = 'builder'
        builder = Builder.objects.get(name=builder)
        context['builder'] = builder

    elif master:
        render_template = 'master'
        master = Master.objects.get(name=master)
        context['master'] = master
    else:
        context['hosts'] = Host.objects.exclude(id=1)
    return render_to_response('loki/%s.html' % render_template, context,
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def action(request, action, master, slave=None):
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


def _config_save(request, bot_id, type):
    cfg_obj, cfg_param_obj = cfg_objs[type]
    id_str = '%sid' % type
    num_str = '%s_num' % type
    result = ''
    if request.method == 'POST':
        builder = Builder.objects.get(id=bot_id)
        data = request.POST.copy()
        # get a config or create a newone
        if id_str in data and data[id_str]:
            cfg_obj = cfg_obj.objects.get(id=data[id_str])
            cfg_obj.num = data[num_str]
            del data[id_str]
            del data[num_str]
        else:
            config = Config.objects.get(id=data['config_type_id'])
            cfg_obj = cfg_obj(builder=builder, type=config, num=data['config_num'])
            cfg_obj.save()
            del data['config_type_id']
            del data['config_num']

        params_2_add = []
        # add and upate params
        params = cfg_obj.params.all()
        for p, v in data.items():
            v = type_sniffer(v)
            param_type = ConfigParam.objects.get(id=p)
            s = cfg_obj.params.filter(type=param_type)
            if s:
                s = s[0]
                s.val = pickle.dumps(v)
                s.default=(v==param_type.loads_default())
                s.save()
            else:
                param = StepParam(step=step, type=param_type,
                                  val=pickle.dumps(v),
                                  default=(v==param_type.loads_default()))
                params_2_add.append(param)
        if params_2_add:
            cfg_obj.params = params_2_add
        cfg_obj.save()
        result = cfg_obj.id
    return HttpResponse(result)


@user_passes_test(lambda u: u.is_superuser)
def config_step_save(request, bot_id):
    return _config_save(request, bot_id, 'step')


@user_passes_test(lambda u: u.is_superuser)
def config_status_save(request, bot_id):
    return _config_save(request, bot_id, 'status')


@user_passes_test(lambda u: u.is_superuser)
def config_scheduler_save(request, bot_id):
    return _config_save(request, bot_id, 'scheduler')


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
