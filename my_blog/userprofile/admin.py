from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
from .models import Profile


class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False
	verbose_name_plural = '附加信息'


class UserAdmin(BaseUserAdmin):
	inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)