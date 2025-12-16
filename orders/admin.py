from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity', 'get_cost']
    can_delete = False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'total_price', 'status', 'is_paid', 'created_at']
    list_editable = ['status', 'is_paid']
    list_filter = ['status', 'is_paid', 'created_at']
    search_fields = ['full_name', 'phone_number', 'transaction_id']
    readonly_fields = ['total_price', 'transaction_id']
    inlines = [OrderItemInline]

    # اکشن‌های سریع برای تغییر وضعیت
    actions = ['mark_as_sent', 'mark_as_cancelled']

    @admin.action(description="تغییر وضعیت به ارسال شده")
    def mark_as_sent(self, request, queryset):
        queryset.update(status=Order.Status.SENT)

    @admin.action(description="لغو سفارش (موجودی برمی‌گردد)")
    def mark_as_cancelled(self, request, queryset):
        # برای اینکه سیگنال بازگشت موجودی اجرا شود، باید تک به تک ذخیره کنیم
        for order in queryset:
            order.status = Order.Status.CANCELLED
            order.save()