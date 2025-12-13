from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from .models import ProductAttribute, Category, Product


@staff_member_required
def get_category_attributes(request, category_id):
    # 1. پیدا کردن دسته‌بندی انتخاب شده
    current_category = get_object_or_404(Category, id=category_id)

    # 2. پیدا کردن تمام اجداد (پدر، پدر بزرگ و...)
    category_family_ids = [current_category.id]
    parent = current_category.parent

    # تا وقتی که پدر وجود دارد، برو بالا
    while parent:
        category_family_ids.append(parent.id)
        parent = parent.parent

    # 3. گرفتن ویژگی‌هایی که متعلق به این خانواده هستند
    attributes = ProductAttribute.objects.filter(
        category_id__in=category_family_ids
    ).values('key', 'label')

    return JsonResponse({'attributes': list(attributes)})


def product_list(request):
    """
    صفحه نمایش محصولات با قابلیت فیلتر بر اساس کوئری استرینگ
    """
    products = Product.objects.filter(status=Product.Status.PUBLISHED, is_available=True)

    # --- فیلترهای ساده ---

    # 1. فیلتر بر اساس دسته‌بندی (Slug)
    category_slug = request.GET.get('category')
    if category_slug:
        # استفاده از get_descendants برای گرفتن محصولات زیرمجموعه هم
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category__in=category.get_descendants(include_self=True))

    # 2. فیلتر بر اساس برند
    brand_slug = request.GET.get('brand')
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    # 3. جستجو
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)

    context = {
        'products': products,
    }
    return render(request, 'products/product_list.html', context)