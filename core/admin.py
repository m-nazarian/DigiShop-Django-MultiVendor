from django.contrib import admin
from django.utils.html import format_html
from .models import Slider, HomeBanner


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'is_active']
    list_editable = ['is_active']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto; border-radius: 5px;" />',
                               obj.image.url)
        return "-"

    image_preview.short_description = "پیش‌نمایش"


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'image_preview', 'is_active', 'order']
    list_filter = ['position', 'is_active']
    list_editable = ['order', 'is_active']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 80px; height: auto; border-radius: 5px;" />', obj.image.url)
        return "-"

    image_preview.short_description = "پیش‌نمایش"