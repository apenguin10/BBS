"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views
from django.views.static import serve
from BBS import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/', views.register, name='register'),  # 注册
    url(r'^login/', views.login, name='login'),  # 登录
    url(r'^get_code/', views.get_code, name='get_code'),  # 图片验证码
    url(r'^home/', views.home, name='home'),  # 首页
    url(r'^setpwd/', views.set_password, name="set_pwd"),  # 修改密码
    url(r'^logout/', views.logout, name='logout'),  # 注销

    # 点赞点踩页
    url(r'^up_or_down/', views.up_or_down),

    # 文章评论
    url(r'^comment/', views.comment),

    # 后台管理
    url(r'^backend/', views.backend),
    url(r'^add/article/', views.add_article),
    url(r'^add/category/', views.add_category),
    url(r'^add/tag/', views.add_tag),
    url(r'^edit_article/', views.edit_article),
    url(r'^delete_article/', views.delete_article),
    url(r'^upload_image/', views.upload_image),

    # 修改用户头像
    url('^set/avatar/', views.set_avatar),

    # 暴露后端指定文件夹资源
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),

    # 个人站点页面搭建
    url(r'^(?P<username>\w+)/$', views.site),

    # 侧边栏筛选
    # url(r'^(?P<username>\w+)/category/(\d+)/', views.site),
    # url(r'^(?P<username>\w+)/tag/(\d+)/', views.site),
    # url(r'^(?P<username>\w+)/archive/(\w+)/', views.site),

    # 合并
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site),

    # 文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail),

    # 返回404
    url(r'^(.*)/', views.error),
]
