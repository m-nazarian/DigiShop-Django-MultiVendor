from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User, Vendor


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # تنظیمات نمایش لیست کاربران
    list_display = ['phone_number', 'full_name', 'is_staff', 'is_verified']
    search_fields = ['phone_number', 'full_name']
    ordering = ['phone_number']

    # چون username نداریم، باید فیلدها رو اصلاح کنیم
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password'),
        }),
    )


@admin.register(Vendor)
class VendorAdmin(ModelAdmin):
    list_display = ['store_name', 'user', 'status', 'commission_rate', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['store_name', 'user__phone_number']
    prepopulated_fields = {'slug': ('store_name',)}

    actions = ['approve_vendors', 'suspend_vendors']

    # اکشن برای تایید گروهی فروشندگان
    @admin.action(description='Approve selected vendors')
    def approve_vendors(self, request, queryset):
        queryset.update(status=Vendor.Status.ACTIVE)

    @admin.action(description='Suspend selected vendors')
    def suspend_vendors(self, request, queryset):
        queryset.update(status=Vendor.Status.SUSPENDED)