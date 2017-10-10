# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import markdown
from django.utils.html import strip_tags
# Create your models here.
#分类
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

#标签
class Tag(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=100) #文章标题
    body = models.TextField()                #文章正文
    created_time = models.DateField()        #创建时间
    modified_time = models.DateField()       #最后修改时间
    excerpt = models.CharField(max_length=200,blank=True)   #文章摘要
    category = models.ForeignKey(Category)                  #分类与文章一对多，外键
    tags = models.ManyToManyField(Tag,blank=True)           #标签与文章多对多
    author = models.ForeignKey(User)                        #作者与文章一对多，
    views = models.PositiveIntegerField(default=0)          #阅读量
    # django.contrib.auth专门用于处理网站用户的注册，登录等流程
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('blog:detail',kwargs={'pk':self.pk})

    def increase_views(self):
        self.views+=1
        self.save(update_fields=['views'])  #只更新数据库中 views 字段

    '''
    复写模型的save方法，在数据被保存到数据库前，
    先从 body 字段摘取N个字符保存到excerpt字段中，
    从而实现自动摘要
    '''
    def save(self, *args,**kwargs):
        # 如果没有填写摘要
        if not self.excerpt:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]
        super(Post,self).save(*args,**kwargs)

    class Meta:
        ordering = ['-created_time']
