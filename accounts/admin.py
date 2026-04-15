from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser  


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display  = ['email', 'role', 'is_active', 'is_staff']
    list_filter   = ['role', 'is_active']
    search_fields = ['email']
    ordering      = ['email']

    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Role',         {'fields': ('role',)}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'password1', 'password2', 'role'),
        }),
    )

    filter_horizontal = ()