# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,get_object_or_404,redirect
from blog.models import Post

from .models import Comment
from .forms import CommentForm

# Create your views here.
def post_comment(request,post_pk):
    post = get_object_or_404(Post,pk=post_pk)

    if request.method == 'POST':
        #用户提交的数据存在request.POSY中，这是一个类字典对象
        form = CommentForm(request.POST)

        # 当调用 form.is_valid() 方法时，Django 自动帮我们检查表单的数据是否符合格式要求。
        if form.is_valid():
            # commit=False 的作用是仅仅利用表单的数据生成 Comment 模型类的实例，但还不保存评论数据到数据库。
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            # 重定向到 post 的详情页，实际上当 redirect 函数接收一个模型的实例时，它会调用这个模型实例的 get_absolute_url 方法，
            # 然后重定向到 get_absolute_url 方法返回的 URL。
            print ('form is valid')
            return redirect(post)
        else:
            # 注意这里我们用到了 post.comment_set.all() 方法，
            # 这个用法有点类似于 Post.objects.all()
            # 其作用是获取这篇 post 下的的全部评论，
            # 因为 Post 和 Comment 是 ForeignKey 关联的，
            # 因此使用 post.comment_set.all() 反向查询全部评论。
            comment_list = post.comment_set.all()
            context = {
                'post':post,
                'form':form,
                'comment_list':comment_list
            }
            print ('form is not valid')
            return render(request,'blog/detail.html',context=context)
    print ('no form')
    return redirect(post)