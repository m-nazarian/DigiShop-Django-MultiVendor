from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


# --- تنظیمات فارسی سازی پنل ---
admin.site.site_header = "مدیریت فروشگاه دیجی‌شاپ"
admin.site.site_title = "پنل مدیریت"
admin.site.index_title = "خوش آمدید به داشبورد مدیریت"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('', include('core.urls')),
    path('orders/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),

]

# تنظیمات نمایش فایل‌های استاتیک و مدیا در حالت DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)