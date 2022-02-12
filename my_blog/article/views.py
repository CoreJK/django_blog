from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q

# 认证应用
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

import markdown

from .forms import ArticlePostForm
from .models import ArticlePost

from comment.models import ArticleComment

def article_list(request):
	"""首页展示所有文章"""
	# 根据GET请求中查询条件
	# 返回不同排序的对象列表
	search = request.GET.get('search')
	order = request.GET.get('order')
	if search:
		if order == 'total_views':
			# Q 对象 进行联合搜索
			article_list = ArticlePost.objects.filter(
				Q(title__icontains=search) |
				Q(body__icontains=search)
			).order_by('-total_views')
		else:
			article_list = ArticlePost.objects.filter(
				Q(title__icontains=search) |
				Q(body__icontains=search)
			)
	else:
		# 将 search 参数重置为空
		search = ''
		if order == 'total_views':
			article_list = ArticlePost.objects.all().order_by('-total_views')
		else:
			article_list = ArticlePost.objects.all()


	# 文章分页展示
	paginator = Paginator(article_list, 2)
	page = request.GET.get('page')
	articles = paginator.get_page(page)
	context = {'articles': articles, 'order': order, 'search': search}

	return render(request, 'article/list.html', context)


def article_detail(request, id):
	"""阅读指定文章"""
	# 取出相应文章
	article = ArticlePost.objects.get(id=id)
	# 浏览量 +1
	if request.user != article.author:
	# 保证作者每次修改和阅读，不给自己增加阅读量
		article.total_views += 1
		article.save(update_fields=['total_views'])

	# 修改 Markdown 语法渲染
	md = markdown.Markdown(
		extensions = [
				'markdown.extensions.extra',
				'markdown.extensions.codehilite',
				'markdown.extensions.toc',
			]
		)
	article.body = md.convert(article.body)

	# 获取文章的评论
	comments = ArticleComment.objects.filter(article=id)
	# 需要传递给模板的对象
	context = {'article': article, 'toc': md.toc, 'comments': comments}
	# 载入模板，并返回 context 对象
	return render(request, 'article/detail.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
	"""创建一篇文章"""
	# 判断用户是否提交数据
	if request.method == "POST":
		# 将提交的数据赋值到表单实例中
		article_post_form = ArticlePostForm(data=request.POST)
		# 根据请求中用户的 id 
		author_name = request.user.id
		# 判断提交的数据是否满足模型要求
		if article_post_form.is_valid():
			# 保存数据，但暂时不提交到数据库中
			new_article = article_post_form.save(commit=False)
			# 通过id获取当前登录的用户名，作为文章署名
			new_article.author = User.objects.get(id=author_name)
			# 将文章保存到数据库中
			new_article.save()
			# 完成后返回到文章列表
			return redirect("article:article_list")
		# 如果数据不合法，返回错误信息
		else:
			return HttpResponse("表单内容有无，请重新填写。")
	# 用户请求写文章
	else:
		# 创建表单实列
		article_post_form = ArticlePostForm()
		# 赋值上下文
		context = {'aritcle_post_form': article_post_form}
		# 返回模板
		return render(request, 'article/create.html', context)


@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
	"""不安全的删除文章"""
	# 根据条件选择要删除的文章
	article = ArticlePost.objects.get(id=id)
	article.delete()
	return redirect("article:article_list")


@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
	"""安全删除文章"""
	if request.method == 'POST':
		article = ArticlePost.objects.get(pk=id)
		article.delete()
		return redirect("article:article_list")
	else:
		return HttpResponse("仅允许post请求")


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
	"""更新文章视图"""
	article = ArticlePost.objects.get(pk=id)

	# 过滤非作者用户修改文章
	if request.user != article.author:
		return HttpResponse("抱歉，你无权修改这篇文章。")

	if request.method == "POST":
		article_post_form = ArticlePostForm(data=request.POST)
		if article_post_form.is_valid():
			article.title = request.POST.get('title')
			article.body = request.POST.get('body')
			article.save()
			return redirect('article:article_detail', id=id)
		else:
			HttpResponse("请检查输入内容是否有误！并重新填写相关内容。")
	else:
		article_post_form = ArticlePostForm()
		context = {'article': article, 'article_post_form': article_post_form}
		return render(request, 'article/update.html', context)
