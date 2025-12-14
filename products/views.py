from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from .models import ProductAttribute, Category, Product, Brand, AttributeGroup, Review
from .forms import ReviewForm
from django.db.models import Count, Q


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
            values = products.values_list(f'specifications__{spec_key}', flat=True).distinct()
            clean_values = [v for v in values if v]
            if clean_values:
                filterable_specs.append({
                    'key': spec_key,
                    'label': attr.label,
                    'values': sorted(clean_values)
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

    context = {
        'product': product,
        'specs_display': specs_display,
        'summary_specs': summary_specs,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'range_5': range(1, 6),
        'form': form,
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