# -*- coding: utf-8 -*-

from django.contrib import admin

from orders.models import *


admin.site.register(OrderDay)
admin.site.register(Article)
admin.site.register(Cost)
admin.site.register(Order)
admin.site.register(DeliveredOrder)
admin.site.register(CostOrder)
admin.site.register(Printout)
