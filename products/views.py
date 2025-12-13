from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from .models import ProductAttribute, Category, Product, Brand


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
    products = Product.objects.filter(status=Product.Status.PUBLISHED)

    # --- فیلترهای پایه ---

    # 1. دسته‌بندی
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category__in=category.get_descendants(include_self=True))

    # 2. برند (چند انتخابی)
    brands_slugs = request.GET.getlist('brand')
    if brands_slugs:
        products = products.filter(brand__slug__in=brands_slugs)

    # 3. جستجو
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # 4. موجودی
    if request.GET.get('available') == '1':
        products = products.filter(stock__gt=0)

    # 5. مرتب‌سازی
    sort_by = request.GET.get('sort')
    if sort_by == 'cheapest':
        products = products.order_by('price')
    elif sort_by == 'expensive':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    # --- ارسال دیتای مورد نیاز به قالب ---
    context = {
        'products': products,
        'brands': Brand.objects.all(),
    }
    return render(request, 'products/product_list.html', context)