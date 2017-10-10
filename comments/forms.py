# -*- coding: utf-8 -*-
from django import forms
from .models import Comment

#Django 的表单类必须继承自 forms.Form 类或者 forms.ModelForm 类
#如果表单对应有一个数据库模型,那么使用 ModelForm 类会简单很多
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment #表单对应的数据库模型
        fields = ['name','email','url','text']
