from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Role, User, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'get_roles', 'created_at')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('created_at', 'updated_at', 'deleted_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

    def get_roles(self, obj):
        return ", ".join([user_role.role.role for user_role in obj.user_roles.all()])

    get_roles.short_description = 'Roles'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'created_at')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')




