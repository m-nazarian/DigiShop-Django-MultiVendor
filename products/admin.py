from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Brand, Product, ProductImage, Category, Review, ProductAttribute


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1  # تعداد فیلدهای خالی پیش‌فرض
    tab = True  # نمایش به صورت تب در Unfold


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'image_preview']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'parent']
    inlines = [ProductAttributeInline]

    def image_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" style="width: 30px; height: 30px; border-radius: 50%;" />', obj.icon.url)
        return "-"

    image_preview.short_description = "Icon"


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ['name', 'logo_preview']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="width: 40px; height: auto;" />', obj.logo.url)
        return "-"

    logo_preview.short_description = "Logo"


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    # 1. اضافه کردن wishlist_count به لیست نمایش
    list_display = ['name', 'price_display', 'vendor', 'category', 'status', 'wishlist_count', 'cover_preview']
    list_filter = ['status', 'is_available', 'created_at', 'vendor', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    # 2. اضافه کردن قابلیت سرچ برای انتخاب کاربران
    autocomplete_fields = ['wishlist']

    inlines = [ProductImageInline]

    fieldsets = (
        ("General Info", {
            "fields": ("name", "slug", "vendor", "category", "brand", "description")
        }),
        ("Pricing & Stock", {
            "fields": ("price", "discount_price", "stock"),
            "classes": ("tab",),
        }),
        ("Details", {
            "fields": ("image", "specifications", "status", "is_available"),
        }),
        # 3. اضافه کردن بخش علاقه‌مندی‌ها به صفحه ویرایش
        ("Engagement", {
            "fields": ("wishlist",),
            "classes": ("collapse",),  # به صورت جمع‌شده نمایش داده میشه
        }),
    )

    class Media:
        js = ('js/admin_specifications.js',)


    def price_display(self, obj):
        return f"{obj.price:,} Toman"

    price_display.short_description = "Price"

    def cover_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url)
        return "-"

    cover_preview.short_description = "Cover"

    # متد محاسبه تعداد لایک‌ها
    def wishlist_count(self, obj):
        return obj.wishlist.count()

    wishlist_count.short_description = "❤️ Likes"
    wishlist_count.admin_order_field = 'wishlist'  # قابلیت سورت کردن بر اساس تعداد لایک