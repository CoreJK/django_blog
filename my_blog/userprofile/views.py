from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import UserLoginForm, UserRegisterForm, ProfileForm
from .models import Profile


def user_login(request):
	if request.method == "POST":
		user_login_form = UserLoginForm(data=request.POST)
		if user_login_form.is_valid():
			# .cleaned_data 清洗出合法数据,返回包含字段的字典，也就是一致的格式
			data = user_login_form.cleaned_data
			# 检验账号、密码是否正确匹配数据库中的某个用户
			user = authenticate(username=data['username'], password=data['password'])
			if user:
				# 用户数据保存在 session 中，即实现了登录动作
				login(request, user)
				return redirect("article:article_list")
			else:
				return HttpResponse("账号或密码输入错误。请重新输入~")
		else:
			return HttpResponse("账号或密码输入不合法")

	elif request.method == 'GET':
		user_login_form = UserLoginForm()
		context = {'form': user_login_form}
		return render(request, 'userprofile/login.html', context)
	else:
		return HttpResponse("请使用 GET 或 POST 请求数据")


def user_logout(request):
	"""用户退出登录"""
	logout(request)
	return redirect("article:article_list")


def user_register(request):
	"""用户注册"""
	if request.method == "POST":
		# 将请求数据传递给表单实例
		user_register_form = UserRegisterForm(data=request.POST)
		if user_register_form.is_valid():
			new_user = user_register_form.save(commit=False)
			new_user.set_password(user_register_form.cleaned_data['password'])
			new_user.save()
			login(request, new_user)
			return redirect("article:article_list")
		else:
			return HttpResponse("注册表单输入有误。请重新输入~")
	elif request.method == 'GET':
		user_register_form = UserRegisterForm()
		context = {'form': user_register_form}
		return render(request, 'userprofile/register.html', context)
	else:
		return HttpResponse("请使用GET或POST请求数据")


# 编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
	user = User.objects.get(pk=id)
	# profile = Profile.objects.get(user_id=id)

	if Profile.objects.filter(user_id=id).exists():
		profile = Profile.objects.get(user_id=id)
	else:
		profile = Profile.objects.create(user=user)

	if request.method == 'POST':
		# 验证修改数据者，是否为用户本人
		if request.user != user:
			return HttpResponse("你没有权限修改此用户信息。")

		# 从 request.FILES 中，通过参数传递给表单类
		profile_form = ProfileForm(request.POST, request.FILES)
		if profile_form.is_valid():
			# 取得清洗后的合法数据
			profile_cd = profile_form.cleaned_data
			# 更新 profile 表
			profile.phone = profile_cd.get('phone')
			profile.bio = profile_cd.get('bio')
			if 'avatar' in request.FILES:
				profile.avatar = profile_cd.get("avatar")
			profile.save()
			# 带参数的 redirect()
			return redirect("userprofile:edit", id=id)
		else:
			return HttpResponse("注册的表单输入有误。请重新输入~")
	elif request.method == 'GET':
		context = {'profile': profile, 'user': user}
		return render(request, 'userprofile/edit.html', context)
	else:
		return HttpResponse("请使用 GET 或 POST　请求数据")
