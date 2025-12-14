from django.db import models
from django.conf import settings


class Slider(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان')
    sub_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='زیرعنوان')
    image = models.ImageField(upload_to='sliders/', verbose_name='تصویر (1920x600)')
    url = models.URLField(max_length=500, verbose_name='لینک مقصد')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'اسلایدر'
        verbose_name_plural = 'اسلایدرها'

    def __str__(self):
        return self.title


class HomeBanner(models.Model):
    class Position(models.TextChoices):
        TOP_RIGHT = 'top_right', 'بالا راست (کنار اسلایدر)'
        TOP_LEFT = 'top_left', 'بالا چپ (کنار اسلایدر)'
        MID_TWO = 'mid_two', 'میانه (۲ تایی)'
        BOTTOM_FOUR = 'bottom_four', 'پایین (۴ تایی)'

    title = models.CharField(max_length=100, verbose_name='عنوان')
    image = models.ImageField(upload_to='banners/', verbose_name='تصویر')
    url = models.URLField(max_length=500, verbose_name='لینک مقصد')
    position = models.CharField(max_length=20, choices=Position.choices, verbose_name='موقعیت نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')

    class Meta:
        ordering = ['order']
        verbose_name = 'بنر تبلیغاتی'
        verbose_name_plural = 'بنرهای تبلیغاتی'

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"



class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تاریخچه جستجو'
        verbose_name_plural = 'تاریخچه جستجوها'

    def __str__(self):
        return f"{self.user} - {self.query}"