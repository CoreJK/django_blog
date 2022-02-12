# 从 django 引入表单类, 和模型类似
from django import forms

# 从 django 自带的用户app 的模型中导入用户的模型
# 表单类和模型一一对应的存在
from django.contrib.auth.models import User
# 引入 Profile 模型
from .models import Profile


# 不修改数据库的字段 只用继承 forms.Form 
class UserLoginForm(forms.Form):
	"""登录表单类，继承了 forms.Form 类"""
	username = forms.CharField()
	password = forms.CharField()

class UserRegisterForm(forms.ModelForm):
	"""用户注册表单类"""
	password = forms.CharField()
	password2 = forms.CharField()

	# 定义表所对应的模型，以及需要修改的字段
	class Meta:
		model = User
		fields = ('username', 'email')

	def clean_password2(self):
		data = self.cleaned_data
		if data.get('password') == data.get('password2'):
			return data.get('password')
		else:
			raise forms.ValidationError("密码输入不一致，请重试。")
		
# 需要对模型发生修改 要从 froms 继承ModelForm		
class ProfileForm(forms.ModelForm):	

	# 还要定义 对应修改的模型名称以及字段
	class Meta:
		model = Profile
		fields = ('phone', 'avatar', 'bio')
		