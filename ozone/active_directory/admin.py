# -*- coding: utf-8 -*-

from django.contrib import admin

from active_directory.models import ADCache


class ADCacheAdmin(admin.ModelAdmin):
    list_display = ('username', 'expires')
    list_display_links = ('username',)
    list_editable = ('expires',)
    ordering = ('-expires',)
    save_on_top = True
    search_fields = ('username',)


admin.site.register(ADCache, ADCacheAdmin)
