from django.db import models
from django.conf import settings
from products.models import Product
from django.core.validators import MinValueValidator


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار پرداخت'
        PROCESSING = 'processing', 'در حال پردازش'
        SENT = 'sent', 'ارسال شده'
        DELIVERED = 'delivered', 'تحویل شده'
        CANCELLED = 'cancelled', 'لغو شده'
        RETURNED = 'returned', 'مرجوع شده'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders',
                             verbose_name='کاربر')

    full_name = models.CharField(max_length=100, verbose_name='نام گیرنده')
    address = models.TextField(verbose_name='آدرس کامل')
    phone_number = models.CharField(max_length=15, verbose_name='شماره تماس')

    total_price = models.PositiveIntegerField(default=0, verbose_name='مبلغ کل')
    is_paid = models.BooleanField(default=False, verbose_name='وضعیت پرداخت')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='وضعیت سفارش')

    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='کد تراکنش')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'

    def __str__(self):
        return f"سفارش {self.id} - {self.user.phone_number}"

    def get_total_cost(self):
        return self.total_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='سفارش')
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name='محصول')
    price = models.PositiveIntegerField(verbose_name='قیمت واحد')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='تعداد')

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    def get_cost(self):
        price = self.price if self.price is not None else 0
        quantity = self.quantity if self.quantity is not None else 0
        return price * quantity