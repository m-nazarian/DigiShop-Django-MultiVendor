from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import ProductAttribute, Category, Product, Brand, AttributeGroup, Review
from .forms import ReviewForm
from django.contrib import messages
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.utils.text import Truncator


# --- API مربوط به پنل ادمین ---
@staff_member_required
def get_category_attributes(request, category_id):
    current_category = get_object_or_404(Category, id=category_id)
    category_family = current_category.get_ancestors(include_self=True)
    groups = AttributeGroup.objects.filter(
        category__in=category_family
    ).prefetch_related('attributes').order_by('category__level', 'order')

    data = []
    for group in groups:
        attributes = group.attributes.all().values('key', 'label')
        if attributes:
            data.append({
                'group_name': group.name,
                'attributes': list(attributes)
            })
    return JsonResponse({'groups': data})


# --- لیست محصولات ---
def product_list(request):
    products = Product.objects.filter(status=Product.Status.PUBLISHED)
    filterable_specs = []
    current_category = None
    category_slug = request.GET.get('category')

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category__in=current_category.get_descendants(include_self=True))

        category_family_ids = current_category.get_ancestors(include_self=True).values_list('id', flat=True)

        attributes = ProductAttribute.objects.filter(
            group__category_id__in=category_family_ids,
            is_filterable=True
        )

        for attr in attributes:
            spec_key = attr.key

            raw_values = products.values_list(f'specifications__{spec_key}', flat=True)

            # استفاده از set برای حذف تکراری‌های واقعی
            clean_values_set = set()

            for val in raw_values:
                if val:
                    # تبدیل به رشته و حذف فاصله‌های اول و آخر
                    clean_val = str(val).strip()
                    if clean_val:
                        clean_values_set.add(clean_val)

            if clean_values_set:
                filterable_specs.append({
                    'key': spec_key,
                    'label': attr.label,
                    'values': sorted(list(clean_values_set))
                })

    brands_slugs = request.GET.getlist('brand')
    if brands_slugs:
        products = products.filter(brand__slug__in=brands_slugs)

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(name__icontains=search_query)

    if request.GET.get('available') == '1':
        products = products.filter(stock__gt=0)

    for param in request.GET:
        if param.startswith('spec_'):
            clean_key = param.replace('spec_', '')
            selected_values = request.GET.getlist(param)
            if selected_values:
                filter_kwargs = {f"specifications__{clean_key}__in": selected_values}
                products = products.filter(**filter_kwargs)

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


# --- جزئیات محصول ---
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('vendor', 'category', 'brand')
        .prefetch_related('images', 'reviews__user'),
        slug=slug,
        status=Product.Status.PUBLISHED
    )

    category_family = product.category.get_ancestors(include_self=True)

    main_attrs = ProductAttribute.objects.filter(
        group__category__in=category_family,
        is_main=True
    ).order_by('group__order', 'order')

    summary_specs = []
    for attr in main_attrs:
        value = product.specifications.get(attr.key)
        if value:
            summary_specs.append({
                'label': attr.label,
                'value': value
            })

    summary_specs = summary_specs[:6]


    attribute_groups = AttributeGroup.objects.filter(category__in=category_family).prefetch_related('attributes')

    specs_display = []
    for group in attribute_groups:
        group_specs = []
        for attr in group.attributes.all():
            value = product.specifications.get(attr.key)
            if value:
                group_specs.append({'label': attr.label, 'value': value})
        if group_specs:
            specs_display.append({'name': group.name, 'items': group_specs})

    reviews = product.reviews.all()
    avg_rating = 0
    if reviews.exists():
        avg_rating = sum(r.score for r in reviews) / reviews.count()

    # فرم نظرات
    form = ReviewForm()

    # === محصولات مرتبط ===
    related_products = Product.objects.filter(
        category=product.category,  # هم‌دسته
        status=Product.Status.PUBLISHED,  # منتشر شده
        is_available=True
    ).exclude(id=product.id).order_by('?')[:10]  # خود محصول رو حذف کن، رندوم ۱۰ تا بیار

    context = {
        'product': product,
        'specs_display': specs_display,
        'summary_specs': summary_specs,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'range_5': range(1, 6),
        'form': form,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)



def amazing_offers(request):
    """
    صفحه نمایش تمام محصولات تخفیف‌دار
    اولویت نمایش با محصولاتی است که ادمین تیک is_special زده است.
    """
    products = Product.objects.filter(
        status=Product.Status.PUBLISHED,
        is_available=True,
        stock__gt=0,
        discount_price__isnull=False  # فقط تخفیف‌دارها
    ).order_by(
        '-is_special',   # اول اونایی که ادمین ویژه کرده
        '-created_at'    # بعد جدیدترین‌ها
    )

    context = {
        'products': products
    }
    return render(request, 'products/amazing_offers.html', context)


# 1. تابع کمکی برای رندر کردن جدول
def render_compare_table(request):
    compare_list = request.session.get('compare_list', [])
    products = Product.objects.filter(id__in=compare_list)

    context = {'products': products}

    if products.exists():
        reference_category = products.first().category
        category_family = reference_category.get_ancestors(include_self=True)
        groups = AttributeGroup.objects.filter(category__in=category_family).prefetch_related('attributes').order_by(
            'category__level', 'order')

        comparison_data = []
        for group in groups:
            group_attrs = []
            for attr in group.attributes.all():
                row = {'label': attr.label, 'values': []}
                has_value = False
                for product in products:
                    val = product.specifications.get(attr.key, '-')
                    row['values'].append(val)
                    if val != '-': has_value = True
                if has_value: group_attrs.append(row)
            if group_attrs: comparison_data.append({'group_name': group.name, 'attributes': group_attrs})

        context['comparison_data'] = comparison_data

    # اگر درخواست HTMX بود، فقط پارشیال جدول رو برگردون
    return render(request, 'products/partials/compare_table.html', context)


# 2. ویوی اصلی صفحه مقایسه
def compare_products(request):
    # برای بار اول که صفحه باز میشه، کل قالب رو میفرستیم
    # اما دیتای جدول رو با همون تابع کمکی میسازیم
    response = render_compare_table(request)

    compare_list = request.session.get('compare_list', [])
    products = Product.objects.filter(id__in=compare_list)

    # لاجیک ساخت comparison_data
    comparison_data = []
    if products.exists():
        reference_category = products.first().category
        category_family = reference_category.get_ancestors(include_self=True)
        groups = AttributeGroup.objects.filter(category__in=category_family).prefetch_related('attributes')

        for group in groups:
            group_attrs = []
            for attr in group.attributes.all():
                row = {'label': attr.label, 'values': []}
                has_value = False
                for product in products:
                    val = product.specifications.get(attr.key, '-')
                    row['values'].append(val)
                    if val != '-': has_value = True
                if has_value: group_attrs.append(row)
            if group_attrs: comparison_data.append({'group_name': group.name, 'attributes': group_attrs})

    context = {
        'products': products,
        'comparison_data': comparison_data
    }
    return render(request, 'products/compare.html', context)


# 3. افزودن به مقایسه
def add_to_compare(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    compare_list = request.session.get('compare_list', [])

    msg_text = ""

    short_name = Truncator(product.name).words(6, truncate='...')

    # --- لاجیک بررسی و افزودن ---
    if product_id not in compare_list:
        is_compatible = False
        if not compare_list:
            is_compatible = True
        else:
            first_product = Product.objects.get(id=compare_list[0])
            if product.category == first_product.category:
                is_compatible = True
            else:
                cat1_ancestors = product.category.get_ancestors(include_self=True)
                cat2_ancestors = first_product.category.get_ancestors(include_self=True)
                common_ancestors = set(cat1_ancestors) & set(cat2_ancestors)
                for ancestor in common_ancestors:
                    if ancestor.is_comparison_root:
                        is_compatible = True
                        break

        if is_compatible:
            if len(compare_list) < 4:
                compare_list.append(product_id)
                request.session['compare_list'] = compare_list
                # استفاده از نام کوتاه در پیام موفقیت
                msg_text = f"{short_name} به لیست مقایسه اضافه شد."
            else:
                msg_text = "ظرفیت لیست مقایسه پر است."
        else:
            msg_text = "این محصول با لیست مقایسه هم‌خوانی ندارد."
    else:
        msg_text = f"{short_name} قبلاً در لیست وجود دارد."

    # --- مدیریت پاسخ HTMX ---
    if request.htmx:
        if request.headers.get('HX-Target') == 'compare-table-container':
            table_html = render_compare_table(request).content.decode('utf-8')
            badge_html = render_to_string('core/includes/compare_badge.html', request=request)
            return HttpResponse(table_html + badge_html)

        toast_html = render_to_string('core/includes/toast_oob.html', {'message': msg_text}, request=request)
        badge_html = render_to_string('core/includes/compare_badge.html', request=request)

        return HttpResponse(toast_html + badge_html)

    messages.info(request, msg_text)
    return redirect('products:product_detail', slug=product.slug)


def remove_from_compare(request, product_id):
    compare_list = request.session.get('compare_list', [])
    if product_id in compare_list:
        compare_list.remove(product_id)
        request.session['compare_list'] = compare_list

    if request.htmx:
        # وقتی حذف میکنیم، هم جدول باید آپدیت شه، هم بج بالای صفحه
        table_response = render_compare_table(request)
        table_html = table_response.content.decode('utf-8')

        # رندر کردن بج جدید
        badge_html = render_to_string('core/includes/compare_badge.html', request=request)

        # ارسال هر دو با هم
        return HttpResponse(table_html + badge_html)

    return redirect('products:compare_products')


# 5. جستجو برای مقایسه
def search_for_compare(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return HttpResponse('')

    compare_list = request.session.get('compare_list', [])

    products = Product.objects.filter(name__icontains=query, status=Product.Status.PUBLISHED)

    # اگر لیستی وجود دارد، باید فقط محصولات هم‌دسته را بیاوریم
    if compare_list:
        first_product = Product.objects.get(id=compare_list[0])
        # پیدا کردن دسته‌های مجاز (خود دسته + اجدادی که تیک root دارن)
        valid_categories = [first_product.category]
        ancestors = first_product.category.get_ancestors(include_self=True)

        # اگر یکی از اجداد root باشه، تمام زیرمجموعه‌های اون جد مجازن
        root_category = None
        for anc in ancestors:
            if anc.is_comparison_root:
                root_category = anc
                break

        if root_category:
            products = products.filter(category__in=root_category.get_descendants(include_self=True))
        else:
            # اگر هیچ ریشه‌ای تعریف نشده، فقط دقیقا همون دسته رو بیار
            products = products.filter(category=first_product.category)

    # حذف محصولاتی که الان تو لیست هستن
    products = products.exclude(id__in=compare_list)[:5]

    return render(request, 'products/partials/compare_search_results.html', {'products': products})