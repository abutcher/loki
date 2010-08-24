# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import pickle

from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from loki.settings import *
from loki.bind_administration import bind_administration
from loki.signal_receivers import post_save_bot
from loki.signal_receivers import post_delete_bot
from loki.signal_receivers import post_save_config
from loki.model_helpers import _template
from loki.model_helpers import _generate_class
from loki.model_helpers import build_bot_run

# these are for filters later
# need to try catch them because syncdb
# will fail because it hasn't created the content_type table
# but needs it to ge these types
try:
    status_content_type = ContentType.objects.get(
                            app_label="loki", model="status")
    step_content_type = ContentType.objects.get(
                            app_label="loki", model="step")
    scheduler_content_type = ContentType.objects.get(
                            app_label="loki", model="scheduler")
except:
    status_content_type = step_content_type = scheduler_content_type = 0


class Host(models.Model):
    hostname = models.CharField(max_length=200, unique=True)
    base_dir = models.CharField(max_length=200)
    username = models.CharField(max_length=10, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)

    uptime = property(lambda self: self._uptime())

    def _uptime(self):
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host.hostname,
            username=self.host.username,
            password=self.host.password,
        allow_agent=True, look_for_keys=True)
        stdin, stdout, stderr = ssh.exec_command(command)
        print stdout.readlines()
        print stderr.readlines()
        ssh.close()
        return stdout.readline()

    def __unicode__(self):
        return self.hostname


class Bot(models.Model):

    name = models.SlugField(max_length=25, unique=True)
    alive = property(lambda self: (self.host.id > 1 and self.pid()) or \
                (self.pid() and \
                 os.path.exists(os.path.join('/proc', str(self.pid())))))

    class Meta(object):
        """
        Meta attributes for Package.
        """
        abstract = True

    def bot_run(self, action):
        actions = {
            'start': self.bot_start,
            'stop': self.bot_stop,
            'restart': self.bot_restart,
            'hup': self.bot_reconfig,
            'reconfig': self.bot_reconfig,
            'create': self.bot_create,
        }
        actions[action]()

    def bot_start(self):
        self._run('start')

    def bot_stop(self):
        self._run('stop')
        return 1

    def bot_restart(self):
        self._run('restart')

    def bot_reconfig(self):
        self._run('reconfig')

    def bot_cfg(self):
        self._run('cfg')

    def bot_create(self):
        self._run('create')

    def bot_delete(self):
        if self.host.id == 1:
            if os.path.isdir(self.path):
                import shutil
                shutil.rmtree(self.path)
        else:
            self._run('delete')
        return 1

    def _run(self, action):
        # run commands based on remote or local
        if self.host.id == 1:
            # local bot
            if action == 'cfg':
                content = self.generate_cfg()
                cfg_file = os.path.join(self.path, self.cfg_file)
                cfg = open(cfg_file, 'w')
                cfg.write(content)
                cfg.close()
                action = ''
            elif action == 'create':
                action = self.buildbot_create % self.path
                if not os.path.exists(self.base_path):
                    os.mkdir(self.base_path)
            else:
                action = '%s %s' % (action, self.path)
            if action:
                build_bot_run(action.split(' '))
        else:
            # remote bot
            import paramiko
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host.hostname,
                        username=self.host.username,
                        password=self.host.password,
                allow_agent=True, look_for_keys=True)
            if action == 'cfg':
                content = self.generate_cfg()
                cfg_file = os.path.join(self.path, self.cfg_file)
                sftp = ssh.open_sftp()
                f = sftp.file(cfg_file, 'w')
                f.write(content)
                f.close()
                sftp.close()
            else:
                if action == 'create':
                    command = 'buildbot %s' % self.buildbot_create % self.path
                elif action == 'delete':
                    command = 'rm -rf %s' % self.path
                else:
                    command = 'buildbot %s %s' % (action, self.path)
                stdin, stdout, stderr = ssh.exec_command(command)
                print stdout.readlines()
                print stderr.readlines()
            ssh.close()

    def pid(self):
        pid = 0
        if self.host.id == 1:
            # local bot
            pid_file = os.path.join(self.path, 'twistd.pid')
            if os.path.exists(pid_file):
                pid_fd = open(pid_file, 'r')
                pid = pid_fd.read()
                pid_fd.close()
        else:
            # remote bot
            import paramiko
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host.hostname,
                        username=self.host.username,
                        password=self.host.password,
                allow_agent=True, look_for_keys=True)
            sftp = ssh.open_sftp()
            pid_file = os.path.join(self.path, 'twistd.pid')
            try:
                f = sftp.file(pid_file, 'r')
                pid = f.readline()
                f.close()
            except:
                # for now we'll just assume the file didn't exist
                pass
            sftp.close()
            ssh.close()
        return int(pid)


class Master(Bot):
    host = models.ForeignKey(Host, related_name='masters')
    slave_port = models.IntegerField(max_length=5)
    web_port = models.IntegerField(max_length=5)

    base_path = property(lambda self: os.path.join(self.host.base_dir, \
                                     BUILDBOT_MASTERS))
    path = property(lambda self: os.path.join(self.host.base_dir, \
                                     BUILDBOT_MASTERS, self.name))

    buildbot_create = 'create-master %s'
    cfg_file = 'master.cfg'

    def __unicode__(self):
        return self.name

    def generate_cfg(self):
        buildslaves = ''
        factories = ''
        statuses = ''
        schedulers = ''
        imports = ''
        builders = []
        modules = []
        ct = 1

        for slave in self.slaves.all():
            #generate the BuildSlave objects
            buildslaves += "\n    BuildSlave('%s', '%s')," % \
                (slave.name, slave.passwd)

        for builder in self.builders.all():
            #create buildfactory
            b = '%s_%s' % (self.name, builder.name)
            b = b.replace('-', '__dash__')
            factories += '%s = factory.BuildFactory()\n' % b
            for step in builder.steps.all():
                if step.type not in modules:
                    modules.append(step.type)
                factories += "%s.addStep(%s)\n" % (b,
                                      _generate_class(step))
            #create builder from factory
            slave_list = map(lambda s: str(s.name), builder.slaves.all())
            factories += "b%s = {'name': '%s',\n" % (ct, builder.name)
            factories += "      'slavenames': %s,\n" % slave_list
            factories += "      'builddir': '%s',\n" % builder.name
            factories += "      'factory': %s, }\n\n" % b
            # remember the builders
            builders.append('b%s' % ct)
            ct += 1

        #generate status
        for status in self.status.all():
            statuses += "c['status'].append(%s)" % _generate_class(status)
            modules.append(status.type)

        #generate schedulers
        for scheduler in self.schedulers.all():
            schedulers += (
                "c['scheduler'].append(%s)" % _generate_class(scheduler))
            modules.append(scheduler.type)

        #restructure the imports
        for x in modules:
            imports += 'from %s import %s\n' % (
                        '.'.join(x.module.split('.')[:-1]),
                         x.module.split('.')[-1])

        #generate the template
        return _template('%smaster.cfg.tpl' % BUILDBOT_TMPLS,
                botname=self.name,
                webhost=self.host,
                webport=self.web_port,
                slaveport=self.slave_port,
                buildslaves=buildslaves,
                imports=imports,
                factories=factories,
                builders=','.join(builders),
                statuses=statuses,
                schedulers=schedulers)


class Slave(Bot):
    host = models.ForeignKey(Host, related_name='slaves')
    master = models.ForeignKey(Master, related_name='slaves')
    passwd = models.SlugField(max_length=25)

    base_path = property(lambda self: os.path.join(self.host.base_dir, \
                                     BUILDBOT_SLAVES))
    path = property(lambda self: os.path.join(self.host.base_dir, \
                                     BUILDBOT_SLAVES, self.name))
    buildbot_create = property(lambda self: 'create-slave %%s %s:%s %s %s' % \
        (self.master.host, self.master.slave_port, self.name, self.passwd))
    cfg_file = 'buildbot.tac'

    def __unicode__(self):
        return self.name

    def generate_cfg(self):
        return _template('%sslave.cfg.tpl' % BUILDBOT_TMPLS,
                basedir=os.path.abspath(self.path),
                masterhost=self.master.host,
                slavename=self.name,
                slaveport=self.master.slave_port,
                slavepasswd=self.passwd)


class Builder(models.Model):
    name = models.SlugField(max_length=25, unique=True)
    master = models.ForeignKey(Master, related_name='builders')
    slaves = models.ManyToManyField(Slave, related_name='builders')

    def __unicode__(self):
        return self.name


class Config(models.Model):
    """
    A definition of what configs are available
    """
    name = models.CharField(max_length=25)
    module = models.CharField(max_length=200, unique=True)
    content_type = models.ForeignKey(ContentType)

    def __unicode__(self):
        return self.name


class ConfigParam(models.Model):
    name = models.CharField(max_length=25)
    type = models.ForeignKey(Config, related_name='params')
    default = models.CharField(max_length=200, blank=True, null=True)
    required = models.BooleanField(default=False)

    def loads_default(self):
        try:
            return pickle.loads(str(self.default))
        except:
            return self.default

    def __unicode__(self):
        req = ''
        if self.required:
            req = ' *'
        return '%s :: %s%s' % (self.type, self.name, req)


class Status(models.Model):
    master = models.ForeignKey(Master, related_name='status')
    type = models.ForeignKey(Config, related_name='status_type',
                             limit_choices_to={
                                 'content_type': status_content_type})

    def __unicode__(self):
        return '%s :: %s' % (self.master, self.type)


class StatusParam(models.Model):
    status = models.ForeignKey(Status, related_name='params')
    type = models.ForeignKey(ConfigParam)
    val = models.CharField(max_length=200, blank=True, null=True)
    default = models.BooleanField(default=False)

    def loads_val(self):
        try:
            return pickle.loads(str(self.val))
        except:
            return self.val

    def __unicode__(self):
        return '%s :: %s' % (self.status, self.val)


class Step(models.Model):
    builder = models.ForeignKey(Builder, related_name='steps')
    type = models.ForeignKey(Config, related_name='step_type',
                             limit_choices_to={
                                 'content_type': step_content_type})
    num = models.IntegerField()

    class Meta:
        ordering = ('num', )

    def __unicode__(self):
        return '%s :: %s' % (self.builder, self.type)


class StepParam(models.Model):
    step = models.ForeignKey(Step, related_name='params')
    type = models.ForeignKey(ConfigParam)
    val = models.CharField(max_length=200, blank=True, null=True)
    default = models.BooleanField(default=False)

    def loads_val(self):
        try:
            return pickle.loads(str(self.val))
        except:
            return self.val

    def __unicode__(self):
        return '%s :: %s:%s' % (self.step, self.type.name, self.loads_val())


class Scheduler(models.Model):
    master = models.ForeignKey(Master, related_name='schedulers')
    type = models.ForeignKey(Config, related_name='scheduler_type',
                             limit_choices_to={
                                 'content_type': scheduler_content_type})

    def __unicode__(self):
        return '%s :: %s' % (self.slave, self.type)


class SchedulerParam(models.Model):
    scheduler = models.ForeignKey(Scheduler, related_name='params')
    type = models.ForeignKey(ConfigParam)
    val = models.CharField(max_length=200)
    default = models.BooleanField(default=False)

    def loads_val(self):
        try:
            return pickle.loads(str(self.val))
        except:
            return self.val

    def __unicode__(self):
        return '%s :: %s' % (self.scheduler, self.val)

cfg_objs = {
    'step': (Step, StepParam),
    'status': (Status, StatusParam),
    'scheduler': (Scheduler, SchedulerParam),
}

bind_administration('loki.models', 'loki.admin')
#post_save.connect(post_save_bot, sender=Bot)
#post_delete.connect(post_delete_bot, sender=Bot)
post_save.connect(post_save_bot, sender=Master)
post_delete.connect(post_delete_bot, sender=Master)
post_save.connect(post_save_bot, sender=Slave)
post_delete.connect(post_delete_bot, sender=Slave)
post_save.connect(post_save_config, sender=Builder)
post_save.connect(post_save_config, sender=Step)
post_save.connect(post_save_config, sender=Status)
post_save.connect(post_save_config, sender=Scheduler)
