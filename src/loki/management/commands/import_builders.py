# Copyright 2008, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import pickle

from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from loki.models import step_content_type
from loki.models import Master, Builder, Config
from loki.models import Step, StepParam
from loki.helpers import config_importer

class Command(BaseCommand):
    args = 'path/to/master.cfg'
    help = 'Reads a provided master.cfg file and imports builders'

    option_list = BaseCommand.option_list + (
        make_option('--master',
            dest='master',
            default=None,
            help='The master to add the builder to'),
        make_option('--builder',
            dest='builder',
            default=None,
            help='Skip builder prompt, import this one'),
        make_option('--auto',
            action="store_true",
            dest='auto',
            default=False,
            help='Assume yes to all y/n prompts'),
        )

    def yes_no(self, msg):
        cont = raw_input("%s (y/N) " % msg)
        while cont.upper() not in ['Y', 'N', '']:
            cont = raw_input("%s Please type y or n " % msg)
        return cont.upper() == 'Y'

    def handle(self, *args, **options):
        # import the master config and throw away what we don't need
        m_cfg = {}
        execfile(args[0], m_cfg)
        m_cfg = m_cfg['c']

        # massage builder data struct
        builders = {}
        for i in m_cfg['builders']:
            builders[i['name']] = i

        if options['builder']:
            builder = options['builder']
        else:
            # ask what builder to import
            print "Builders:"
            for i in builders:
                print ' - %s' % i
            builder = raw_input("\nWhich builder would you like to import? ")

        # verify steps
        print '\nVerifying Steps for builder %s:' % builder
        x = 1
        for ct, i in enumerate(builders[builder]['factory'].steps):
            print '%s: %s' % (ct+1, str(i[0]))
            for o in i[1].items():
                print '    %s: %s' % o

        if not options['auto'] and not self.yes_no("Import these steps?"):
            exit(0)

        print '\nVerifying that step objects are registered:'
        step_types = {}
        for i in builders[builder]['factory'].steps:
            try:
                if str(i[0]) not in step_types:
                    step_types[str(i[0])] = Config.objects.get(module=str(i[0]),
                                                    content_type=step_content_type)
                print ' - %s: registered' % str(i[0])
            except:
                print '\n%s is not registered with loki\n' % str(i[0])
                if options['auto'] or self.yes_no("Import %s definition?" % str(i[0])):
                    config_importer(str(i[0]), 'steps')
                    if str(i[0]) not in step_types:
                        step_types[str(i[0])] = Config.objects.get(module=str(i[0]),
                                                        content_type=step_content_type)
                    print ' - %s: imported' % str(i[0])
                else:
                    print '\nCannot continue without registering \
%s definition with loki\n' % str(i[0])
                    exit(1)

        # do the builder import
        print '\nImporting builder %s' % builder
        master = Master.objects.get(name=options['master']) 
        builder = Builder(name=builder, master=master)
        builder.save()
        try:
            builder.slaves = master.slaves.all()
            builder.save()
            for i, s in enumerate(builders[builder.name]['factory'].steps):
                step = Step(builder=builder, type=step_types[str(s[0])], num=i+1)
                step.save()
                for p in step_types[str(s[0])].params.all():
                    if p.name in s[1]:
                        param = StepParam(step=step, type=p, val=pickle.dumps(s[1][p.name]),
                              default=(s[1][p.name]==p.loads_default()))
                    else:
                        print '%s %s not defined in config being imported, using default: %s' % \
                              (s[0], p.name, p.loads_default())
                        param = StepParam(step=step, type=p, val=p.default, default=True)
                    param.save() 
            print '\nImport Complete\n\n'
        except Exception, e:
            #something failed so let's not leave the builder half imported
            builder.delete()
            print '\nImport Failed!'
            raise e
