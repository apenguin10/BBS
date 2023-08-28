# test
python、django


# 1 表设计

```python
# 一个项目中最重要的部分，前期的表设计

bbs 表设计
	- 用户表
    	- 继承AbstractUser
        - 拓展
        	- phone		电话号码
            - avatar	用户头像
            - create_time	创建时间
         
        = 外键字段
        	= 一对一个人站点表
        
    - 个人站点表
    	- site_name		站点名称
        - site_title	站点标题
        - site_theme	站点样式      
        
    - 文章标签表
    	- name	标签名
        
        = 外键字段
        	= 一对多个人站点
        
    - 文章分类表
    	- name	分类名
        
        = 外键字段
        	= 一对多个人站点
    
    - 文章表
    	- title			文章标题
        - desc			文章简介
        - content		文章内容
        - create_time	发布时间
        
        # 数据库字段设计优化(虽然下述的三个字段可以从其他表里面跨表查询计算得出，但是频繁跨表效率)
        - up_num		点赞数
        - down_num		点踩数
        - comment_num	评论数
        
        = 外键字段
        	= 一对多个人站点
            = 多对多文章标签
            = 一对多文章分类表
    
    - 点赞点踩表
    	# 记录哪个用户给哪篇文章点了赞还是点了踩
        - user			ForeignKey(to="User")
        - article		ForeignKey(to="Article")
        - is_up			BooleanField()
    
    - 文章评论表
    	# 用来记录哪个用户给哪篇文章写了哪些评论内容
        - user				ForeignKey(to="User")
        - article			ForeignKey(to="Article")
        - content			CharField()
        - comment_time		DateField()
        
        # 自关联
        - parent			ForeignKey(to="Comment", null=True)
        # ORM专门提供的自关联写法
        - parent			ForeignKey(to="self", null=True)
        
	id	  user_id			     article_id			 parent_id
	1		 1						1										
	2		 2						1			    	1
         
        
根评论子评论的概念
	根评论就是直接评论当前发布的内容的
		
	子评论是评论别人的评论
		1.PHP是世界上最牛逼的语言
			1.1 python才是最牛逼的
				1.2 java才是
		
	根评论与子评论是一对多的关系
    
```
