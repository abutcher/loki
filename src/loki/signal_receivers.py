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

from loki.settings import *
from loki.helpers import generate_master_cfg
from buildbot.scripts.runner import Options, createMaster


def post_save_bot(sender, instance, created, **kwargs):
    """
    post save call back

    :Parameters:
       - sender: the sending object.
       - instance: instance of the object being saved
       - created: if a new record was created
       - kwargs: any keyword arguments
    """
    # create bot if new
    if created:
        instance.bot_create()

    # update the config file
    instance.bot_cfg()

    if hasattr(instance, 'master'):
        instance.master.bot_cfg()
        if instance.master.alive:
            instance.master.bot_reconfig()

    if instance.alive:
        instance.bot_reconfig()


def post_delete_bot(sender, instance, **kwargs):
    """
    post delete call back

    :Parameters:
       - sender: the sending object.
       - instance: instance of the object being saved
       - kwargs: any keyword arguments
    """
    if instance.alive:
        instance.bot_stop()

    # delete bot
    instance.bot_delete()


def post_save_config(sender, instance, **kwargs):
    """
    post save call back

    :Parameters:
       - sender: the sending object.
       - instance: instance of the object being saved
       - created: if a new record was created
       - kwargs: any keyword arguments
    """
    # find the master
    if hasattr(instance, 'master'):
        master = instance.master
    else:
        master = instance.builder.master

    # regen and hup
    master.bot_cfg()
    if master.alive:
        master.bot_reconfig()
