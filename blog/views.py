# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render,get_object_or_404
from .models import Post,Category,Tag
import markdown
from comments.forms import CommentForm
from django.views.generic import ListView,DetailView
from django.utils.text import slugify #可以处理标题中的中文
from markdown.extensions.toc import TocExtension
from django.db.models import Q
# Create your views here.

def index(request):
    post_list = Post.objects.all()
    return render(request, 'blog/index.html', context={'post_list': post_list})

class indexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 5  # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章

    def get_context_data(self, **kwargs):
        # 在类视图中，这个需要传递的模板变量字典是通过get_context_data获得
        context = super(indexView,self).get_context_data(**kwargs)
        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        pagination_data = self.pagination_data(paginator,page,is_paginated)

        context.update(pagination_data)

        return context

    def pagination_data(self,paginator,page,is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
            return {}
        # 当前页左,右边连续的页码号，初始值为空
        left = []
        right = []
        left_has_more = False    # 标示第 1 页页码后是否需要显示省略号
        right_has_more = False      # 标示最后一 页页码后是否需要显示省略号
        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False
        last = False
        page_number = page.number

        total_pages = paginator.num_pages
        page_range = list(paginator.page_range)   # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]

        if page_number == 1:
            right = page_range[page_number:page_number+2]
            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
            if right[-1] < total_pages-1:
                right_has_more = True
                # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
                # 所以需要显示最后一页的页码号，通过 last 来指示
            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            print page_range

            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            #left = page_range[(page_number-3) if (page_number-3) > 0 else 0:page_number-1]
            if left[0]>2:
                left_has_more = True
            if left[0]>1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number+2]

            if left[0] > 2:
                left_has_more =True
            if left[0] > 1:
                first = True

        data = {
            'left':left,
            'right':right,
            'left_has_more':left_has_more,
            'right_has_more':right_has_more,
            'first':first,
            'last':last,
        }
        return data

def detail(request,pk):
    #当传入的 pk 对应的 Post 在数据库存在时，就返回对应的 post，如果不存在，就给用户返回一个 404 错误
    post = get_object_or_404(Post,pk=pk)
    post.increase_views()        #阅读量加1

    post.body = markdown.markdown(post.body,extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {
        'post':post,
        'form':form,
        'comment_list':comment_list
    }
    return render(request,'blog/detail.html',context=context)

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView,self).get(request,*args,**kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super(PostDetailView,self).get_object(queryset=None)
        md = markdown.markdown(post.body, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify),       #美化目录中标题的锚点 URL
            #'markdown.extensions.toc',  #通过 [TOC] 标记在文章内容中插入目录。
        ])
        post.body = md.convert(post.body) #将markdown文本转为HTML文本，同时md对象有了toc属性
        post.toc = md.toc         #给post对象动态添加toc属性,并传给模板
        return post

    def get_context_data(self, **kwargs):
        # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（DetailView 已经帮我们完成），
        # 还要把评论表单、post 下的评论列表传递给模板。
        context = super(PostDetailView,self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context

    # def archives(request,year,month):
#     post_list = Post.objects.filter(created_time__year=year,created_time__month=month)
#     return render(request,'blog/index.html',context={'post_list':post_list})
class archivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return super(archivesView,self).get_queryset().filter(created_time__year=self.kwargs.get('year'),created_time__month=self.kwargs.get('month'))

class categoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category,pk=self.kwargs.get('pk'))
        return super(categoryView,self).get_queryset().filter(category = cate)

# def category(request,pk):
#     cate = get_object_or_404(Category,pk=pk)
#     post_list = Post.objects.filter(category=cate)
#     return render(request, 'blog/index.html', context={'post_list': post_list})

class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag,pk = self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag )

def search(request):
    q = request.GET.get('q') #q是表单中input的name的值
    error_msg = ''

    if not Q:
        error_msg = "请输入关键词"
        return render(request,'blog/index.html',{'error_msg':error_msg})
    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request,'blog/index.html',{'error_msg':error_msg,
                                             'post_list':post_list})