from django import forms
from .models import ArticleComment

class CommentForm(forms.ModelForm):
	class Meta:
		model = ArticleComment
		fields = ['body']