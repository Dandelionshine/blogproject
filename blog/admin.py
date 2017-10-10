# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Post,Category,Tag
import sys
reload(sys)
sys.setdefaultencoding("utf8")

# Register your models here.
class postAdmin(admin.ModelAdmin):
    list_display = ['title','created_time','modified_time','category','author']

admin.site.register(Post,postAdmin)
admin.site.register(Category)
admin.site.register(Tag)