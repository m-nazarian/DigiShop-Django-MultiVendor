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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')

    full_name = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)

    total_price = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # برای پیگیری تراکنش
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.user.phone_number}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.PositiveIntegerField()  # قیمت در لحظه خرید (Snapshot)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        # اگر قیمت یا تعداد None بود، صفر در نظر بگیر
        price = self.price if self.price else 0
        quantity = self.quantity if self.quantity else 0
        return price * quantity