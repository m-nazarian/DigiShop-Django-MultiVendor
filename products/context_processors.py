from .models import Category


def menu_categories(request):
    """
    این تابع دسته‌بندی‌های ریشه (Level 0) را به همراه
    فرزندان و ستون‌های مگا‌منو لود می‌کند تا در هدر نمایش داده شوند.
    """
    # فقط دسته‌های اصلی که فعال هستند
    # prefetch_related برای جلوگیری از کوئری‌های تکراری (N+1 Problem)
    root_categories = Category.objects.filter(level=0, is_active=True).prefetch_related(
        'children',  # زیر دسته‌های درختی
        'menu_columns__items',  # ستون‌های مگا‌منو و آیتم‌هایش
    )

    return {
        'main_menu_categories': root_categories
    }