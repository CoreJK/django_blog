from django.urls import path
from . import views

# 用于在 html 文件中，编写超链接，以及从 views.py 反向url找到对应的视图函数
# {% url 'article:article_list'%}
app_name = 'article'

urlpatterns = [
	path('article-list/', views.article_list, name='article_list'),
	path('article-detail/<int:id>/', views.article_detail, name='article_detail'),
	path('article-create/', views.article_create, name='article_create'),
	path('article-delete/<int:id>/', views.article_delete, name='article_delete'),
	path('article-safe-delete/<int:id>/', views.article_safe_delete, name='article_safe_delete'),
	path('article-update/<int:id>/', views.article_update, name='article_update'),
]