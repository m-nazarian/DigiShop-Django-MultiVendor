from django.http import HttpResponse
from django.shortcuts import render
from core.models import HomeBanner, Slider, SearchHistory
from products.models import Product, Category
from django.db.models import Count
from django.contrib.auth.decorators import login_required


def home(request):
    # 1. اسلایدرهای اصلی
    sliders = Slider.objects.filter(is_active=True)

    # 2. بنرها
    banners = HomeBanner.objects.filter(is_active=True).order_by('order')
    context_banners = {
        'top_left': banners.filter(position='top_left')[:2],
        'mid_two': banners.filter(position='mid_two')[:2],
        'bottom_four': banners.filter(position='bottom_four')[:4]
    }

    # 3. محصولات شگفت‌انگیز
    amazing_products = Product.objects.filter(
        status=Product.Status.PUBLISHED,
        is_available=True,
        stock__gt=0,
        is_special=True,
        discount_price__isnull=False
    ).exclude(discount_price=0).order_by('-updated_at')[:10]

    # 4. جدیدترین محصولات
    latest_products = Product.objects.filter(
        status=Product.Status.PUBLISHED,
        is_available=True
    ).order_by('-created_at')[:12]

    context = {
        'sliders': sliders,
        'banners': context_banners,
        'amazing_products': amazing_products,
        'latest_products': latest_products,
    }
    return render(request, 'core/home.html', context)


def search_box(request):
    query = request.GET.get('q', '').strip()

    if not query:
        recent_searches = []
        if request.user.is_authenticated:
            recent_searches = SearchHistory.objects.filter(user=request.user).values('id', 'query').distinct()[:5]

        popular_searches = ["آیفون 13", "کفش ورزشی", "لپ تاپ ایسوس", "ساعت هوشمند"]

        return render(request, 'core/includes/search_initial.html', {
            'recent_searches': recent_searches,
            'popular_searches': popular_searches
        })

    related_categories = Category.objects.filter(
        products__name__icontains=query,
        products__status=Product.Status.PUBLISHED
    ).annotate(count=Count('id')).filter(count__gt=0).distinct()[:3]

    suggestions = Product.objects.filter(
        name__icontains=query,
        status=Product.Status.PUBLISHED
    ).only('name', 'slug', 'image', 'price', 'discount_price')[:5]

    context = {
        'query': query,
        'related_categories': related_categories,
        'suggestions': suggestions,
    }
    return render(request, 'core/includes/search_results.html', context)


@login_required
def remove_history(request, history_id):
    SearchHistory.objects.filter(id=history_id, user=request.user).delete()
    return HttpResponse("")