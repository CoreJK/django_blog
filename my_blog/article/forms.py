# 导入表单类
from django import forms
# 导入文章模型
from .models import ArticlePost


# 文章表单类
class ArticlePostForm(forms.ModelForm):
	"""
	通过该表单类提交的数据，需要直接和数据库交互
	所以需要继承 forms.ModelsForm
	不是单纯的一个表单
	"""
	class Meta:
		# 指明数据模型来源
		model = ArticlePost
		# 定义表单包含的字段
		fields = ('title', 'body')

