from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Account, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Hồ sơ người dùng'
    fk_name = 'account'


@admin.register(Account)
class AccountAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    model = Account

    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'is_verified', 'updated_at'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups'
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Thông tin cá nhân'), {
            'fields': ('first_name', 'last_name', 'email', 'telephone', 'manager')
        }),
        (_('Phân quyền'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Ngày quan trọng'), {
            'fields': ('last_login', 'date_joined', 'updated_at', 'created_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('updated_at', 'created_at')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'account', 'name', 'gender', 'birthday',
        'language', 'timezone', 'updated_at'
    )
    search_fields = ('account__username', 'name', 'first_name', 'last_name')
    list_filter = ('gender', 'language', 'timezone')
