# Copyright 2009, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
loki template tags
"""

import os
import random
import time

from django import template

from loki.forms import StepParamFormSet

register = template.Library()


@register.inclusion_tag('loki/ajax/step.html', takes_context=True)
# The first argument *must* be called "context" here.
def step(context):
    return {'step': context['step'],
            'user': context['user'],
            'form': StepParamFormSet(queryset=context['step'].params.all()), }


@register.inclusion_tag('loki/ajax/status.html', takes_context=True)
def status(context):
    return {'status': context['status'],
            'user': context['user'], }


@register.inclusion_tag('loki/ajax/scheduler.html', takes_context=True)
def scheduler(context):
    return {'scheduler': context['scheduler'],
            'user': context['user'], }
