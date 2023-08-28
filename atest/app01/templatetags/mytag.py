from django import template
from app01 import models
from django.db.models.functions import TruncMonth
from django.db.models import Count


register = template.Library()


@register.inclusion_tag('left_menu.html')
def left_menu(username):
    # 构造侧边栏需要的数据
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    category_list = models.Category.objects.filter(blog=blog). \
        annotate(count_num=Count('article__pk')).values('pk', 'name', 'count_num')
    tag_list = models.Tag.objects.filter(blog=blog). \
        annotate(count_num=Count('article__pk')).values('pk', 'name', 'count_num')
    date_list = models.Article.objects.filter(blog=blog). \
        annotate(month=TruncMonth('create_time')).values('month'). \
        annotate(count_num=Count('pk')).values('month', 'count_num').order_by('-month')
    return locals()


@register.inclusion_tag('eidt_article_val.html')
def eidt_article_menu(article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    return locals()
