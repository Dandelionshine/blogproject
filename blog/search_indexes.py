# -*- coding: utf-8 -*-
from haystack import indexes
from .models import Post

'''
django haystack 的规定
要相对某个 app 下的数据进行全文检索，
就要在该 app 下创建一个 search_indexes.py 文件，
然后创建一个 XXIndex 类（XX 为含有被检索数据的模型，如这里的 Post），
并且继承 SearchIndex 和 Indexable。
'''

class PostIndex(indexes.SearchIndex,indexes.Indexable):
    text = indexes.CharField(document=True,use_template=True)
    #use_template = True在text字段中，这样就允许我们使用数据模板去建立搜索引擎索引的文件
    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.all()