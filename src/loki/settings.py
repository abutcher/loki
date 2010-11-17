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
import loki

from django.conf import settings

BUILDBOT_TMPLS = str(loki).split()[3][1:-14]
if BUILDBOT_TMPLS[-1] != '/':
    BUILDBOT_TMPLS = '%s/' % BUILDBOT_TMPLS
BUILDBOT_MASTERS = getattr(settings, 'BUILDBOT_MASTERS', 'masters')
BUILDBOT_SLAVES = getattr(settings, 'BUILDBOT_SLAVES', 'slaves')
BB_SLAVE_PORT_START = getattr(settings, 'BB_SLAVE_PORT_START', 8000)
BB_WEB_PORT_START = getattr(settings, 'BB_WEB_PORT_START', 9000)
