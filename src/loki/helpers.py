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
