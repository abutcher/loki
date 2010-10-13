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

@register.filter
def tablesort(value, cols):
    tbl_srt = []
    row_ct = 0

    if value:
        # calc how many rows are needed
        rows = float(len(value))/cols
        if rows > int(rows):
            rows = int(rows)+1
        else:
            rows = int(rows)
        # build an empty list to return
        for x in range(0, rows*cols):
            tbl_srt.append(None)
        for x, i in enumerate(value):
            tbl_srt[x/rows+row_ct*cols] = i
            if row_ct == rows-1:
                row_ct = 0
            else:
                row_ct += 1
    return tbl_srt
