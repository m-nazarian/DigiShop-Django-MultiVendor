# accounts/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Vendor

@receiver(pre_save, sender=Vendor)
def create_vendor_slug(sender, instance, **kwargs):
    if not instance.slug:
        # ساخت اسلاگ از نام فروشگاه (پشتیبانی از فارسی)
        instance.slug = slugify(instance.store_name, allow_unicode=True)