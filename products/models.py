from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from accounts.models import Vendor
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Category(models.Model):
    """
    دسته بندی درختی (Hierarchical Category)
    مثال: الکترونیک -> موبایل -> سامسونگ
    """
    name = models.CharField(max_length=100, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=True, verbose_name='اسلاگ (آدرس)')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name= 'دسته بندی والد'
    )
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True, verbose_name='آیکون')
    image = models.ImageField(upload_to='categories/images/', blank=True, null=True, verbose_name='تصویر')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['name']

    def __str__(self):
        # نمایش به صورت مسیر کامل: الکترونیک > موبایل
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' > '.join(full_path[::-1])


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام برند')
    slug = models.SlugField(unique=True, verbose_name='اسلاگ')
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name='لوگو')

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'پیش نویس'
        REVIEW = 'review', 'در حال بررسی'
        PUBLISHED = 'published', 'منتشر شده'
        REJECTED = 'rejected', 'رد شده'

    # ارتباط با فروشنده
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('فروشنده')
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name= 'دسته بندی'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name = 'برند',
    )

    name = models.CharField(max_length=255, verbose_name='نام محصول')
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, verbose_name='اسلاگ')
    description = models.TextField(blank=True, verbose_name='توضیحات')

    # تصویر اصلی (کاور)
    image = models.ImageField(upload_to='products/covers/', verbose_name='تصویر اصلی')

    price = models.PositiveIntegerField(verbose_name='قیمت (تومان)')
    discount_price = models.PositiveIntegerField(null=True, blank=True, verbose_name='قیمت با تخفیف')
    stock = models.PositiveIntegerField(default=0, verbose_name='موجودی انبار')

    # ویژگی‌های داینامیک
    # مثال دیتا: {"ram": "8GB", "screen": "6.5 inch", "color": "Blue"}
    specifications = models.JSONField(default=dict, blank=True, verbose_name='ویژگی های داینامیک')

    is_available = models.BooleanField(default=True, verbose_name='موجود است؟')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='وضعیت'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    wishlist = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='wishlist',
        blank=True,
        verbose_name=_('Wishlist')
    )

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        """قیمت نهایی با احتساب تخفیف"""
        return self.discount_price if self.discount_price else self.price

    def get_absolute_url(self):
        return reverse('core:product_detail', args=[self.slug])



class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=100, blank=True)
    is_cover = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"


class Review(models.Model):
    class Recommendation(models.TextChoices):
        RECOMMENDED = 'recommended', _('I suggest this product')
        NOT_RECOMMENDED = 'not_recommended', _('I do not suggest this product')
        NO_IDEA = 'no_idea', _('No opinion')

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='امتیاز')
    comment = models.TextField(_('Comment'))

    recommendation = models.CharField(
        max_length=20,
        choices=Recommendation.choices,
        default=Recommendation.NO_IDEA,
        verbose_name = 'پیشنهاد خرید'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # لایک و دیس‌لایک
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reviews', blank=True)
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_reviews', blank=True)

    class Meta:
        verbose_name = 'دیدگاه'
        verbose_name_plural = 'دیدگاه‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} on {self.product}"

    @property
    def is_buyer(self):
        return True