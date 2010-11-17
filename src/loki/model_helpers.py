# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys
import os
import inspect
import pickle

from types import StringType
from types import UnicodeType

from django.conf import settings
from buildbot.scripts.runner import Options
from buildbot.scripts.runner import createMaster
from buildbot.scripts.runner import createSlave
from buildbot.scripts.runner import restart
from buildbot.scripts.runner import stop
from buildbot.interfaces import BuildbotNotRunningError
from twisted.python import usage

from loki.thread import BuildBotStart

loki_pwd = os.path.abspath('.')


def _generate_class(cls):
    """
    TODO: Document me!
    """
    gcls = cls.type.module.split('.')[-1]
    gprm = []
    for param in cls.params.all():
        if type(param.loads_val()) == StringType \
                or type(param.loads_val()) == UnicodeType:
            pair_form = "%s='%s'"
        # buildbot doesn't like unicode added this case to the
        # case above
        #elif type(param.loads_val()) == UnicodeType:
        #    pair_form = "%s=u'%s'"
        else:
            pair_form = "%s=%s"
        gprm.append(pair_form % (param.type.name,
                        param.loads_val()))
    return "%s(%s)" % (gcls, ', '.join(gprm))


def introspect_module(path='buildbot.steps'):
    """
    Get a list of tuples representing classes for config
    each tuple will have the name of a class in the module
    a list of required parameters and
    a dict of optional parameters and their defaults

    @param obj: a python package or module path
    @type obj: module

    @return: dict of tuples 'ClassName'
             : ('classpath', ['reqs'], {'opts': None})
    """
    #x = __import__(pkg, fromlist=['module'])
    x = __import__(path, globals(), locals(), [str(path)])

    modules = []
    #Check if x is a directory and get it's modules
    if hasattr(x, '__path__'):
        for f in os.listdir(x.__path__[0]):
            if f.endswith('.py') and f != '__init__.py':
                modules.append(f.split('.')[0])
    #or it is a module so adjust
    else:
        modules.append(path.split('.')[-1])
        path = '.'.join(path.split('.')[0:-1])


    classes = {}
    for m in modules:
        #y = __import__("%s.%s" % (pkg, m), fromlist=['module'])
        y = __import__("%s.%s" % (path, m),
                       globals(), locals(), ['module'])
        for i in inspect.getmembers(y):
            if inspect.isclass(i[1]) and not i[0].startswith('_')\
               and i[1].__module__.startswith("%s.%s" % (path, m))\
               and (hasattr(i[1], '__init__') and \
                   'method' in str(type(i[1].__init__))):
                req = []
                opt = {}
                i_init = inspect.getargspec(i[1].__init__)
                i_init_args = [x for x in reversed(i_init[0][1:])]
                if i_init[3] != None:
                    i_init_defaults = [x for x in reversed(i_init[3])]
                c = 0
                for a in i_init_args:
                    if i_init[3] == None:
                        req.append(a)
                    else:
                        if c < len(i_init_defaults):
                            if i_init_defaults[c] == None:
                                opt[a] = None
                                # XMLRPC can't handle None, this was used when
                                #we were using func to do this.
                                #opt[a] = 'LokiNone'
                            else:
                                opt[a] = i_init_defaults[c]
                        else:
                            req.append(a)
                    c = c + 1
                classes[i[0]] = ("%s.%s" % (i[1].__module__, i[0]),
                                 req,
                                 opt)
    return classes


def build_bot_run(options):
    if '--quiet' not in options and not settings.DEBUG:
        options.insert(1, '--quiet')
    config = Options()
    try:
        config.parseOptions(options=options)
    except usage.error, e:
        print "%s:  %s" % (options[0], e)
        print
        c = getattr(config, 'subOptions', config)
        print str(c)
        return 1

    command = config.subCommand
    so = config.subOptions

    if command == "create-master":
        createMaster(so)
    elif command == "upgrade-master":
        upgradeMaster(so)
    elif command == "create-slave":
        createSlave(so)

    ## following adapted from
    ## http://stackoverflow.com/questions/972362/spawning-process-from-python
    ## similar recipe http://code.activestate.com/recipes/278731/
    elif command in ["start", "restart", "reconfig", "sighup"]: 
        child_pid = os.fork()
        if child_pid == 0:
            # forked child becomes session leader
            os.setsid()
            g_child_pid = os.fork()
            if g_child_pid == 0:
                # second forked process now a non-session-leader,
                # detached from parent, must now close all open files
                try:
                    maxfd = os.sysconf("SC_OPEN_MAX")
                except (AttributeError, ValueError):
                    maxfd = 1024

                f = open('%stwistd.log' % options[1], 'a')
                sys.stdout = f
                sys.stderr = f

                for fd in range(maxfd):
                    try:
                        os.close(fd)
                    except OSError:
                    # ERROR, fd wasn't open to begin with (ignored)
                        pass

                try:
                    # try and rename myself to buildbot
                    import dl
                    libc = dl.open('/lib/libc.so.6')
                    libc.call('prctl', 15, 'buildbot', 0, 0, 0)
                except:
                    # pass for now, this is kinda experimental
                    pass

                # finally execute the buildbot command
                if command == "start":
                    from buildbot.scripts.startup import start
                    start(so)
                elif command == "restart":
                    restart(so)
                elif command == "reconfig" or command == "sighup":
                    from buildbot.scripts.reconfig import Reconfigurator
                    Reconfigurator().run(so)
                f.close()
                os._exit(0)
            else:
                # done with child process
                os._exit(0)
        else:
            os.waitpid(child_pid, 0)

    elif command == "stop":
        try:
            stop(so, wait=True)
        except BuildbotNotRunningError:
            pass
        except OSError:
            pass
    # moved up into the daemon code
    #elif command == "restart":
    #    restart(so)
    #elif command == "reconfig" or command == "sighup":
    #    from buildbot.scripts.reconfig import Reconfigurator
    #    Reconfigurator().run(so)
    elif command == "sendchange":
        sendchange(so, True)
    elif command == "debugclient":
        debugclient(so)
    elif command == "statuslog":
        statuslog(so)
    elif command == "statusgui":
        statusgui(so)
    elif command == "try":
        doTry(so)
    elif command == "tryserver":
        doTryServer(so)
    elif command == "checkconfig":
        doCheckConfig(so)

    os.chdir(loki_pwd)
