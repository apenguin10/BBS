from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, F
from django.db.models.functions import TruncMonth
from app01.myforms import MyRegForm
from app01 import models
from BBS import settings
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO, StringIO
from bs4 import BeautifulSoup
from app01.utils.page import Pagination
from app01.utils.search import q_serach
import json
import uuid
import random
import os


# Create your views here.


def register(request):
    form_obj = MyRegForm()
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code': 1000, 'msg': ''}
            # 校验数据是否合法
            form_obj = MyRegForm(request.POST)
            if form_obj.is_valid():
                clean_data = form_obj.cleaned_data  # 校验通过的数据字典赋值给变量
                # 将字典里面的confirm_password 键值对删除
                clean_data.pop('confirm_password')  # 3个键值对
                # 用户头像
                file_obj = request.FILES.get("avatar")
                if file_obj:
                    uid = str(uuid.uuid4())
                    suid = ''.join(uid.split('-'))
                    file_obj.name = "{}{}".format(suid, file_obj.name)
                    clean_data['avatar'] = file_obj
                # 操作数据库保存数据
                models.UserInfo.objects.create_user(**clean_data)
                back_dic['url'] = '/login/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = form_obj.errors
            return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


def login(request):
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code': 1000, 'msg': ''}
            username = request.POST.get('username')
            password = request.POST.get('password')
            code = request.POST.get('code')
            # 1. 先校验验证码是否正确, 自己决定是否忽略大小写
            if request.session.get('code').upper() == code.upper():
                # 2. 校验用户名和密码是否正确
                user_obj = auth.authenticate(request, username=username, password=password)
                if user_obj:
                    auth.login(request, user_obj)
                    back_dic['url'] = '/home/'
                else:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '用户名或密码错误'
            else:
                back_dic['code'] = 3000
                back_dic['msg'] = '验证码错误'
            return JsonResponse(back_dic)

    return render(request, 'login.html', locals())


def get_code(request):
    def get_random():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 推导步骤1, 直接获取后端现成的图片二进制数据发送给前端
    # with open(r'static/img/aaa.jpg', 'rb') as f:
    #     data = f.read()

    # 推导步骤2, 利用pillow模块动态产生图片
    # img_obj = Image.new('RGB', (460, 33), get_random())
    # # 先将图片对象保存起来
    # with open('xxx.png', 'wb') as f:
    #     img_obj.save(f, 'png')
    # # 再将图片对象读取出来
    # with open('xxx.png', 'rb') as f:
    #     data = f.read()

    # # 推导步骤3: 文件存储繁琐IO操作效率低, 借助内存模块
    # img_obj = Image.new('RGB', (460, 33), get_random())
    # io_obj = BytesIO()  # 生成一个内存管理器对象(可以看作文件句柄)
    # img_obj.save(io_obj, 'png')
    # return HttpResponse(io_obj.getvalue())  # 从内存管理器中读取二进制的图片数据返回给前端

    # 推导步骤4: 写图片验证码
    img_obj = Image.new('RGB', (215, 33), get_random())
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/333.ttf', 28)  # 字体样式 大小

    # 随机验证码 四位数的随机验证码 数字 小写字母 大写字母
    code = ''
    for i in range(4):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = chr(random.randint(48, 57))
        # 从上面三个随机选择一个
        tmp = random.choice([random_upper, random_lower, random_int])
        # 将产生的随机字符串写入到图片上
        """
        为什么一个个写而不是生成好了之后再写？
        因为一个个写能够控制每个字体的间隙 而生成好之后再写的话
        间隙就没法控制了
        """
        img_draw.text((30 + i * 45, -3), tmp, get_random(), img_font)
        # 拼接随机字符串
        code += tmp

    # 随机验证码在登录的视图函数里面需要用到 要比对 需要存起来，并且其它视图函数也需要
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):

    search = request.GET.get('search')
    if search:
        article_queryset = models.Article.objects.filter(q_serach(search)).order_by('-create_time')
    else:
        article_queryset = models.Article.objects.order_by('-create_time')
    # 查询本网站所有的文章数据展示到前端页面 这里可以使用分页器作分页
    current_page = request.GET.get('page', 1)
    all_count = article_queryset.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    page_queryset = article_queryset[page_obj.start: page_obj.end]
    return render(request, 'home.html', locals())


@login_required
def set_password(request):
    back_dic = {'code': 0}
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code': 1000, 'msg': ''}
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            if is_right:
                if new_password == old_password:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '新密码与原密码一致'
                elif new_password == confirm_password:
                    if len(new_password) == 0:
                        back_dic['code'] = 2000
                        back_dic['msg'] = '新密码不能为空'
                    elif len(new_password) < 6:
                        back_dic['code'] = 2000
                        back_dic['msg'] = '新密码最少为6位'
                    elif len(new_password) > 12:
                        back_dic['code'] = 2000
                        back_dic['msg'] = '新密码最多为12位'
                    else:
                        request.user.set_password(new_password)
                        request.user.save()
                        user_obj = auth.authenticate(request, username=request.user.username, password=new_password)
                        auth.login(request, user_obj)
                        back_dic['msg'] = '修改成功'
                        back_dic['url'] = '/login/'
                else:
                    back_dic['code'] = 3000
                    back_dic['msg'] = '新密码和确认密码不一致'
            else:
                if len(old_password) == 0:
                    back_dic['code'] = 4000
                    back_dic['msg'] = '原密码不能为空'
                else:
                    back_dic['code'] = 4000
                    back_dic['msg'] = '原密码错误'
            return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')


def site(request, username, **kwargs):
    """
    :param request:
    :param username:
    :param kwargs: 如果该参数有zhi
    :return:
    """
    # 1. 先校验当前用户名对应的个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 2. 用户不存在, 返回404页面
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    # 查询当前个人站点下的所有文章
    search = request.GET.get('search')
    if search:
        article_list = models.Article.objects.filter(blog=blog).filter(q_serach(search)).order_by('-create_time')
    else:
        article_list = models.Article.objects.filter(blog=blog).order_by('-create_time')
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 判断用户到底想要按照哪个条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    # # 1. 查询当前用户所有的分类及分类下的文章数
    # category_list = models.Category.objects.filter(blog=blog). \
    #     annotate(count_num=Count('article__pk')).values('pk', 'name', 'count_num')
    # # 2. 查询当前用户所有的标签及标签下的文章数
    # tag_list = models.Tag.objects.filter(blog=blog).\
    #     annotate(count_num=Count('article__pk')).values('pk', 'name', 'count_num')
    # # 3. 查询当前用户所有的按照年月统计的所有文章数
    # date_list = models.Article.objects.filter(blog=blog).\
    #     annotate(month=TruncMonth('create_time')).values('month').\
    #     annotate(count_num=Count('pk')).values('month', 'count_num').order_by('-month')
    # 分页
    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    page_queryset = article_list[page_obj.start: page_obj.end]
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    """
    校验username 和 article_id是否存在, 不存在则返回404
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    if not (article_obj and user_obj):
        return render(request, 'error.html')
    comment_list = models.Comment.objects.filter(article=article_obj).order_by('comment_time')
    return render(request, 'article_detail.html', locals())


def up_or_down(request):
    """
    1. 登录的用户可以点赞点踩
    2. 判断当前文章是否是当前用户自己写的(自己不能点自己的文章)
    3. 当前用户是否已经给当前文章点过了
    4. 操作数据库
    :param request:
    :return:
    """
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code': 1000, 'msg': ''}
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                is_up = request.POST.get('is_up')   # true <class 'str'>
                is_up = json.loads(is_up)
                article_obj = models.Article.objects.filter(pk=article_id).first()
                if not article_obj.blog.userinfo == request.user:
                    is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj).first()
                    if not is_click:
                        if is_up:
                            # 点赞数加一
                            models.Article.objects.filter(pk=article_id).update(up_num = F('up_num') + 1)
                            back_dic['msg'] = '点赞成功'
                        else:
                            # 点踩数加一
                            models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                            back_dic['msg'] = '点踩成功'
                        models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                    else:
                        back_dic['code'] = 1001
                        back_dic['msg'] = '你已经点过赞了' if is_click.is_up else '你已经点过踩了'
                else:
                    back_dic['code'] = 1002
                    back_dic['msg'] = '你无法推荐自己的内容' if is_up else '你无法点踩自己的内容'
            else:
                back_dic['code'] = 1003
                back_dic['msg'] = '请先<a href="/login/">登录</a>'

            return JsonResponse(back_dic)


def comment(request):
    """
    自己也可以评论自己的文章
    :param request:
    :return:
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                if len(content) == 0:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '评论不能为空'
                else:
                    with transaction.atomic():
                        models.Article.objects.filter(pk=article_id)\
                            .update(comment_num=F('comment_num') + 1)
                        models.Comment.objects.create(user=request.user,
                                                      article_id=article_id,
                                                      content=content,
                                                      parent_id=parent_id
                                                      )
                    back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '用户未登录'
            return JsonResponse(back_dic)


@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    category_list = models.Category.objects.filter(blog=request.user.blog)
    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    page_queryset = article_list[page_obj.start: page_obj.end]
    return render(request, 'backend.html', locals())


@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')
        soup = BeautifulSoup(content, "html.parser")
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()    # 删除标签
        # 文章简介
        # 先简单的暴力窃取content 100个字符
        if not (title and content and category_id and tag_id_list):
            return redirect('/add/article/')
        if len(content) > 100:
            desc = soup.text[0: 100]
        else:
            desc = str(soup)
        article_obj = models.Article.objects.create(
            title=title,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            blog=request.user.blog,
        )
        article_obj_list = []
        for i in tag_id_list:
            article_obj_list.append(models.ArticleToTag(article=article_obj, tag_id=i))
        models.ArticleToTag.objects.bulk_create(article_obj_list)
        return redirect('/backend/?page=%s' % request.GET.get('page', 1))
    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    return render(request, 'backend_add_article.html', locals())


@login_required
def edit_article(request):
    article_id = request.GET.get('pk')
    article_obj = models.Article.objects.filter(pk=article_id).first()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')
        soup = BeautifulSoup(content, "html.parser")
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()    # 删除标签
        # 文章简介
        # 先简单的暴力窃取content 100个字符
        if not (title and content and category_id and tag_id_list):
            return redirect('/add/article/')
        if len(content) > 100:
            desc = soup.text[0: 100]
        else:
            desc = str(soup)
        models.Article.objects.filter(pk=article_id).update(
            title=title,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            blog=request.user.blog,
        )
        models.ArticleToTag.objects.filter(article=article_obj).delete()
        article_obj_list = []
        for i in tag_id_list:
            article_obj_list.append(models.ArticleToTag(article=article_obj, tag_id=i))
        models.ArticleToTag.objects.bulk_create(article_obj_list)
        return redirect('/backend/?page=%s' % request.GET.get('page', 1))
    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)

    return render(request, 'backend_edit_article.html', locals())


@login_required
def delete_article(request):
    article_id = request.GET.get('pk')
    models.Article.objects.filter(pk=article_id).delete()
    return redirect('/backend/?page=%s' % request.GET.get('page', 1))


def upload_image(request):
    """
    POST参数
    imgFile: 文件form名称
    dir: 上传类型，分别为image、flash、media、file
    :param request:
    :return:    //成功时
                {
                        "error" : 0,
                        "url" : "http://www.example.com/path/to/file.ext"
                }
                //失败时
                {
                        "error" : 1,
                        "message" : "错误信息"
                }
    """
    back_dic = {
        "error": 0,
    }
    # 用户写文章上传的图片 也算是静态资源 也应该防盗media文件夹下
    if request.method == 'POST':
        # 获取用户上传的图片对象
        file_obj = request.FILES.get('imgFile')
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        uid = str(uuid.uuid4())
        suid = ''.join(uid.split('-'))
        file_obj.name = "{}{}".format(suid, file_obj.name)
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)

        back_dic['url'] = '/media/article_img/%s' % file_obj.name
    return JsonResponse(back_dic)


@login_required
def add_category(request):
    if request.method == 'POST':
        category_content = request.POST.get('category_content')
        if not category_content:
            return redirect('/add/category/')
        models.Category.objects.create(name=category_content, blog=request.user.blog)
        return redirect('/backend/')
    return render(request, 'backend_add_category.html', locals())


@login_required
def add_tag(request):
    if request.method == 'POST':
        tag_content = request.POST.get('tag_content')
        if not tag_content:
            return redirect('/add/tag/')
        models.Tag.objects.create(name=tag_content, blog=request.user.blog)
        return redirect('/backend/')
    return render(request, 'backend_add_tag.html', locals())


@login_required
def set_avatar(request):
    blog = request.user.blog
    username = request.user.username
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        uid = str(uuid.uuid4())
        suid = ''.join(uid.split('-'))
        file_obj.name = "{}{}".format(suid, file_obj.name)
        # 问题 .update 不会字段加avatar前缀
        # 1. 方式1 自己手动加
        # 2， 方式2 user_obj.avatar = file_obj  userobj.save()
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        redirect('/home/')
    return render(request, 'set_avatar.html', locals())


def error(request, args):
    error_url_ = args
    return render(request, 'error.html')
