# -*- coding: utf-8 -*-
from ..models import Post,Category,Tag
from django import template
from django.db.models.aggregates import Count
#将函数注册为模板标签
register =template.Library()

@register.simple_tag()
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_time')[:num]

@register.simple_tag()
def archives():
    #dates 方法会返回一个列表，列表中的元素为每一篇文章（Post）的创建时间，精确到月份，降序排列
    return Post.objects.dates('created_time','month',order='DESC')

@register.simple_tag()
def get_categories():
    # 过滤掉分类数为0的分类
    return Category.objects.annotate(num_posts = Count('post')).filter(num_posts__gt=0)

@register.simple_tag()
def get_tags():
    return Tag.objects.annotate(num_posts = Count('post')).filter(num_posts__gt=0)