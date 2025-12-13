from django.db import models
from django.conf import settings
from products.models import Product
from django.core.validators import MinValueValidator


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار پرداخت'
        PAID = 'paid', 'پرداخت شده (در حال پردازش)'
        SENT = 'sent', 'ارسال شده'
        CANCELLED = 'cancelled', 'لغو شده'
        RETURNED = 'returned', 'مرجوع شده'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')

    full_name = models.CharField(max_length=100, verbose_name='نام گیرنده')
    address = models.TextField(verbose_name='آدرس کامل')
    phone_number = models.CharField(max_length=15, verbose_name='شماره تماس')

    total_price = models.PositiveIntegerField(default=0, verbose_name='مبلغ کل')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده؟')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='وضعیت سفارش')

    # برای پیگیری تراکنش
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='کد تراکنش')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'

    def __str__(self):
        return f"Order {self.id} - {self.user.phone_number}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name='محصول')
    price = models.PositiveIntegerField(verbose_name='قیمت واحد')  # قیمت در لحظه خرید (Snapshot)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='تعداد')

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        # اگر قیمت یا تعداد None بود، صفر در نظر بگیر
        price = self.price if self.price else 0
        quantity = self.quantity if self.quantity else 0
        return price * quantity