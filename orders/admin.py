# -*- coding: utf-8 -*-

from django.contrib import admin

from orders.models import *


class OrderDayAdmin(admin.ModelAdmin):
    list_display = ('day', 'user')
    list_display_links = ('day',)
    list_editable = ('user',)
    list_filter = ('day',)
    ordering = ('day', 'user__last_name')
    search_fields = ('user__last_name', 'user__username')


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'ident', 'quantity', 'price')
    list_display_links = ('name',)
    list_editable = ('ident', 'quantity', 'price')
    list_filter = ('supplier__name',)
    ordering = ('supplier__name', 'name')
    search_fields = ('name', 'supplier__name', 'ident')
    save_on_top = True


class OrderAdmin(admin.ModelAdmin):
    list_display = ('article', 'count', 'memo', 'added', 'order_day', 'state')
    list_display_links = ('article',)
    list_editable = ('count', 'order_day', 'state')
    list_filter = ('order_day', 'state')
    ordering = ('order_day', 'article__name')
    search_fields = ('article__name', 'article__supplier__name')
    save_on_top = True


class DeliveredOrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'count', 'date', 'user')
    list_display_links = ('order',)
    list_editable = ('count',)
    list_filter = ('order', 'date')
    search_fields = ('order__article__name',)
    ordering = ('-order__ordered', '-date')


class PrintoutAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'order_day', 'generated', 'internal')
    list_display_links = ('company_name',)
    list_filter = ('order_day', 'internal')
    search_fields = ('company_name',)
    ordering = ('generated', 'company_name')


admin.site.register(OrderDay, OrderDayAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Cost)
admin.site.register(Order, OrderAdmin)
admin.site.register(DeliveredOrder, DeliveredOrderAdmin)
admin.site.register(CostOrder)
admin.site.register(Printout, PrintoutAdmin)
