from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import Order


@receiver(pre_save, sender=Order)
def manage_stock_on_status_change(sender, instance, **kwargs):
    """
    مدیریت موجودی هنگام تغییر وضعیت سفارش (مثلاً لغو یا مرجوعی)
    """
    if not instance.pk:
        return  # اگر سفارش جدید است کاری نداری

    try:
        old_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    # سناریو ۱: سفارش لغو یا مرجوع می‌شود -> موجودی باید برگردد
    if instance.status in [Order.Status.CANCELLED, Order.Status.RETURNED] and \
            old_order.status not in [Order.Status.CANCELLED, Order.Status.RETURNED]:

        for item in instance.items.all():
            item.product.stock += item.quantity
            item.product.save()

    # سناریو ۲: ادمین اشتباهی لغو کرده و دوباره برمی‌گرداند به پرداخت شده -> موجودی باید کم شود
    elif instance.status == Order.Status.PAID and \
            old_order.status in [Order.Status.CANCELLED, Order.Status.RETURNED]:

        for item in instance.items.all():
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save()
            else:
                pass


@receiver(pre_delete, sender=Order)
def restore_stock_on_delete(sender, instance, **kwargs):
    """
    اگر سفارش حذف شد:
    ۱. اگر پرداخت شده بود -> موجودی برگردد.
    ۲. اگر لغو شده بود -> کاری نکنیم (چون موقع لغو شدن موجودی برگشته).
    """
    if instance.status in [Order.Status.PAID, Order.Status.SENT, Order.Status.PENDING]:

        if instance.is_paid:  # فقط اگر پرداخت موفق بوده موجودی کم شده بوده
            for item in instance.items.all():
                item.product.stock += item.quantity
                item.product.save()