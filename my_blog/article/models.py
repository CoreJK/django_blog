from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone


class ArticlePost(models.Model):
	# 文章作者
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	# 文章标题
	title = models.CharField(max_length=100)
	# 文章正文
	body = models.TextField()
	# 文章阅读量
	total_views = models.PositiveIntegerField(default=0)
	# 文章创建时间
	created = models.DateTimeField(default=timezone.now)
	# 文章更新时间
	updated = models.DateTimeField(auto_now=True)

	# 内部类 Meta ，用于给模型定义元数据
	class Meta:
		# 指定模型返回的数据的排列顺序
		ordering = ('-created',)

	def get_absolute_url(self):
		return reverse('article:article_detail', args=[self.id])

	# 函数 __str__ 定义调用对象的 str()方法时的返回值内容
	def __str__(self):
		# 将文章的标题返回
		return self.title