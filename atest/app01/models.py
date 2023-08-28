from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class UserInfo(AbstractUser):
    """
    用户表信息表
    null=True   数据库该字段可以为空
    blank=True  admin后台管理该字段可以为空
    """
    phone = models.BigIntegerField(verbose_name='用户手机号', null=True, blank=True)
    # 给avatar字段传文件对象,该文件会自动存储到avatar文件下,然后avatar字段只保存文件路径
    avatar = models.FileField(verbose_name='用户头像',
                              upload_to='avatar/',
                              default='avatar/default.png',
                              )
    create_time = models.DateField(verbose_name='用户创建时间', auto_now_add=True)

    blog = models.OneToOneField(verbose_name='一对一Blog表', to='Blog', null=True)

    class Meta:
        """用来修改admin后台管理默认的表名"""
        verbose_name_plural = '用户表'
        # verbose_name = '用户表'      # 默认加s  用户表s

    def __str__(self):
        return self.username


class Blog(models.Model):
    """
    个人站点表
    """
    site_name = models.CharField(verbose_name='站点名称', max_length=32)
    site_title = models.CharField(verbose_name='站点标题', max_length=32)
    # 存css/js的文件路径
    site_theme = models.CharField(verbose_name='站点样式', max_length=256)

    class Meta:
        verbose_name_plural = '个人站点表'

    def __str__(self):
        return self.site_name


class Category(models.Model):
    """
    文章分类表
    """
    name = models.CharField(verbose_name='文章分类', max_length=32)

    blog = models.ForeignKey(verbose_name='多对一Blog表', to='Blog', null=True)

    class Meta:
        verbose_name_plural = '文章分类表'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    文章标签表
    """
    name = models.CharField(verbose_name='文章标签', max_length=32)

    blog = models.ForeignKey(verbose_name='多对一Blog表', to='Blog', null=True)

    class Meta:
        verbose_name_plural = '文章标签表'

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    文章表
    """
    title = models.CharField(verbose_name='文章标题', max_length=64)
    desc = models.CharField(verbose_name='文章简介', max_length=255)
    # 文章内容很多, 一般使用TextField
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateTimeField(verbose_name='文章创建时间', auto_now_add=True)
    # 数据库字段设计优化
    up_num = models.BigIntegerField(verbose_name='文章点赞数', default=0)
    down_num = models.BigIntegerField(verbose_name='文章点踩数', default=0)
    comment_num = models.BigIntegerField(verbose_name='文章评论数', default=0)

    blog = models.ForeignKey(verbose_name='多对一Blog表', to='Blog', null=True)
    category = models.ForeignKey(verbose_name='一对多Category表', to='Category', null=True)
    # tag = models.ManyToManyField(verbose_name='多对多Tag表', to='Tag', null=True)
    tags = models.ManyToManyField(to='Tag',
                                  through='ArticleToTag',
                                  through_fields=('article', 'tag'),
                                  )

    class Meta:
        verbose_name_plural = '文章表'

    def __str__(self):
        return self.title


class ArticleToTag(models.Model):
    """
    自己创建文章和标签的多对多关系表
    """
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')

    class Meta:
        verbose_name_plural = '文章标签关系表'


class UpAndDown(models.Model):
    user = models.ForeignKey(verbose_name='用户', to='UserInfo')
    article = models.ForeignKey(verbose_name='文章', to='Article')
    # 传布尔值存 0/1
    is_up = models.BooleanField(verbose_name='记录用户点赞还是点踩')

    class Meta:
        verbose_name_plural = '点赞点踩表'


class Comment(models.Model):
    user = models.ForeignKey(verbose_name='用户', to='UserInfo')
    article = models.ForeignKey(verbose_name='文章', to='Article')
    content = models.CharField(verbose_name='评论内容', max_length=255)
    comment_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    # 自关联, null=True 有些评论就是根评论
    parent = models.ForeignKey(verbose_name='根评论子评论', to='self', null=True)

    class Meta:
        verbose_name_plural = '评论表'
