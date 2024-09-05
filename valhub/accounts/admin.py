from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Account

# Register your models here.


# Extend the existing UserAdmin class
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        *BaseUserAdmin.fieldsets,
        ("Personal info", {"fields": ("profileImage",)}),
    )


admin.site.register(Account, UserAdmin)
