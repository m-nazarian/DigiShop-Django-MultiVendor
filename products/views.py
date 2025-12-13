from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from .models import ProductAttribute, Category, Product, Brand
from django.db.models import Count, Q


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
    # 1. کوئری پایه: فقط محصولات منتشر شده
    products = Product.objects.filter(status=Product.Status.PUBLISHED)

    # متغیری برای ذخیره ویژگی‌های قابل فیلتر (برای ارسال به تمپلیت)
    filterable_specs = []

    # --- بخش ۱: اعمال فیلترهای پایه ---

    # دسته‌بندی
    current_category = None
    category_slug = request.GET.get('category')

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        # محصولات این دسته و زیرمجموعه‌هاش
        products = products.filter(category__in=current_category.get_descendants(include_self=True))

        # === استخراج فیلترهای پیشرفته ===
        # فقط وقتی دسته‌بندی انتخاب شده، فیلترهای مخصوصش رو نشون میدیم

        # 1. پیدا کردن ویژگی‌های تعریف شده برای این دسته و اجدادش
        category_family_ids = current_category.get_ancestors(include_self=True).values_list('id', flat=True)
        attributes = ProductAttribute.objects.filter(category_id__in=category_family_ids)

        # 2. برای هر ویژگی (مثلا RAM)، مقادیر موجود در محصولات رو پیدا کن
        for attr in attributes:
            spec_key = attr.key

            # پیدا کردن مقادیر یکتا برای این کلید در محصولات فعلی
            values = products.values_list(f'specifications__{spec_key}', flat=True).distinct()

            # حذف مقادیر None یا خالی
            clean_values = [v for v in values if v]

            if clean_values:
                filterable_specs.append({
                    'key': spec_key,
                    'label': attr.label,
                    'values': sorted(clean_values)
                })

    # فیلتر برند
    brands_slugs = request.GET.getlist('brand')
    if brands_slugs:
        products = products.filter(brand__slug__in=brands_slugs)

    # جستجو
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # موجودی
    if request.GET.get('available') == '1':
        products = products.filter(stock__gt=0)

    # === بخش ۲: اعمال فیلترهای پیشرفته (JSON) ===
    # هر پارامتری که با 'spec_' شروع بشه رو میگیریم
    for param in request.GET:
        if param.startswith('spec_'):
            # تبدیل spec_ram به ram
            clean_key = param.replace('spec_', '')
            # دریافت مقادیر انتخاب شده (چون کاربر ممکنه چند تا چک‌باکس بزنه)
            selected_values = request.GET.getlist(param)

            if selected_values:
                # فیلتر کردن روی فیلد JSON
                filter_kwargs = {f"specifications__{clean_key}__in": selected_values}
                products = products.filter(**filter_kwargs)

    # --- مرتب‌سازی (باید آخر همه باشه) ---
    sort_by = request.GET.get('sort')
    if sort_by == 'cheapest':
        products = products.order_by('price')
    elif sort_by == 'expensive':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'brands': Brand.objects.all(),
        'current_category': current_category,
        'filterable_specs': filterable_specs,
    }
    return render(request, 'products/product_list.html', context)