# Copyright 2008-2010, Red Hat, Inc
# Dan Radez <dradez@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from loki.models import *
from django.contrib import admin
from django.contrib.contenttypes import generic


class StepInline(admin.TabularInline):
    model = Step


class StatusParamInline(admin.TabularInline):
    model = StatusParam


class StepParamInline(admin.TabularInline):
    model = StepParam


class SchedulerParamInline(admin.TabularInline):
    model = SchedulerParam


class ConfigParamInline(admin.TabularInline):
    model = ConfigParam


class HostAdmin(admin.ModelAdmin):
    pass


class MasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'slave_port', 'web_port')
    list_display_links = ('name', )


class SlaveAdmin(admin.ModelAdmin):
    list_display = ('name', 'master', 'host')
    list_display_links = ('name', )


class BuilderAdmin(admin.ModelAdmin):
    list_display = ('master', 'name')
    list_display_links = ('name', )
    list_filter = ('master', 'name')
    search_fields = ('name', )
    ordering = ('name', )
    inlines = [StepInline, ]


class ConfigAdmin(admin.ModelAdmin):
    inlines = [ConfigParamInline, ]
    list_display = ('name', 'module', 'content_type')
    search_fields = ('name', 'module')
    ordering = ('name', )


class StatusAdmin(admin.ModelAdmin):
    inlines = [StatusParamInline, ]


class StepAdmin(admin.ModelAdmin):
    inlines = [StepParamInline, ]


class SchedulerAdmin(admin.ModelAdmin):
    inlines = [SchedulerParamInline, ]
