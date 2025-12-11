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
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent Category')
    )
    icon = models.ImageField(upload_to='categories/icons/', blank=True, null=True)
    image = models.ImageField(upload_to='categories/images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
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
    name = models.CharField(_('Brand Name'), max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)

    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        REVIEW = 'review', _('Under Review')
        PUBLISHED = 'published', _('Published')
        REJECTED = 'rejected', _('Rejected')

    # ارتباط با فروشنده
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Vendor')
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Category')
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    name = models.CharField(_('Product Name'), max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(_('Description'), blank=True)

    # تصویر اصلی (کاور)
    image = models.ImageField(upload_to='products/covers/')

    price = models.PositiveIntegerField(_('Price (Toman)'))
    discount_price = models.PositiveIntegerField(_('Discounted Price'), null=True, blank=True)
    stock = models.PositiveIntegerField(_('Stock'), default=0)

    # ویژگی‌های داینامیک
    # مثال دیتا: {"ram": "8GB", "screen": "6.5 inch", "color": "Blue"}
    specifications = models.JSONField(_('Specifications'), default=dict, blank=True)

    is_available = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
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
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Score')
    )
    comment = models.TextField(_('Comment'))
    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reviews', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} on {self.product}"