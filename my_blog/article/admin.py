from django.contrib import admin
# 导入需要在管理员后台编辑的数据表，模型
from .models import ArticlePost

# 在管理员站点中注册需要操作的模型
admin.site.register(ArticlePost)