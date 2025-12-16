from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order


@receiver(pre_save, sender=Order)
def manage_stock_on_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return


    # 1. اگر وضعیت به "در حال پردازش" تغییر کرد (یعنی پرداخت شد) -> موجودی کسر شود
    if instance.status == Order.Status.PROCESSING and old_order.status != Order.Status.PROCESSING:
        for item in instance.items.all():
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save()

    # 2. اگر وضعیت به "لغو شده" تغییر کرد -> موجودی برگردد
    elif instance.status == Order.Status.CANCELLED and old_order.status != Order.Status.CANCELLED:
        for item in instance.items.all():
            item.product.stock += item.quantity
            item.product.save()