# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import pickle

from loki.models import status_content_type
from loki.models import step_content_type
from loki.models import scheduler_content_type
from loki.models import Config, ConfigParam
from loki.model_helpers import introspect_module
from loki.model_helpers import acceptable_functions

def config_importer(module, type):
    content_types = {
        'status': status_content_type,
        'steps': step_content_type,
        'scheduler': scheduler_content_type,
    }
    path = '.'.join(module.split('.')[:-1])
    name = module.split('.')[-1]
    introspected = introspect_module(path=path)
    imported_config = introspected[name]
    new_config = Config(name=name, module=module,
                        content_type=content_types[type])
    new_config.save()
    try:
        for req in imported_config[1]:
            ConfigParam(type=new_config, name=req,
                        required=True).save()
        for opt, default in imported_config[2].items():
            ConfigParam(type=new_config, name=opt,
                        default=pickle.dumps(default)).save()
    except Exception, e:
        new_config.delete()
        raise e

def type_sniffer(value):
    '''
    takes a string as input and casts it to a typed value
    '''
    # If dealing with an acceptable function in a value string, just
    # leave it alone because we don't want to lose the functions
    # formatting.
    for function in acceptable_functions():
        if function in value:
            return value
    value = value.strip()
    if value:
        # strip unicode and force a str
        if value[0] == 'u' and value[1] == value[-1]:
            return str(value[2:-1])
        # force a string
        if value[0] == value[-1] and value[0] in '"\'':
            return str(value[1:-1])
        if value[0] == '{':
            value = value[1:-1]
            value = value.split(',')
            dict = {}
            for i in value:
                i = i.split(':')
                if len(i) == 2:
                    dict[type_sniffer(i[0])] = type_sniffer(i[1])
            return dict
        # assume a list if wrapped with [] or a , is present
        if (value[0] == '[' and value[-1] == ']') or ',' in value:
            if value[0] == '[':
                value=value[1:-1]
            return filter(lambda x: x,
                       map(type_sniffer, value.split(',')))
        # all numbers? cast to an int
        if value.isdigit():
            return int(value)
        # True or False? cast to bool
        if value.upper() == 'TRUE':
            return True
        if value.upper() == 'FALSE':
            return False
        # None? cast to none
        if value.upper() == 'NONE':
            return None
    # it's just a string... return it
    return str(value)
