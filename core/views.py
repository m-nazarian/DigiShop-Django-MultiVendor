from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from core.models import HomeBanner, Slider
from products.models import Product, Review, Category
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from products.forms import ReviewForm
from .models import SearchHistory
from django.db.models import Count, Q


def home(request):
    # 1. اسلایدرهای اصلی
    sliders = Slider.objects.filter(is_active=True)

    # 2. بنرها
    banners = HomeBanner.objects.filter(is_active=True).order_by('order')
    context_banners = {
        'top_left': banners.filter(position='top_left')[:2],  # دو تا بنر سمت چپ اسلایدر
        'mid_two': banners.filter(position='mid_two')[:2],  # بنرهای میانی
        'bottom_four': banners.filter(position='bottom_four')[:4]  # بنرهای پایینی
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


@login_required
@require_POST
def toggle_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if product.wishlist.filter(id=request.user.id).exists():
        product.wishlist.remove(request.user)
    else:
        product.wishlist.add(request.user)
    return render(request, 'core/includes/wishlist_button.html', {'product': product})

@login_required
@require_POST
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        context = {
            'product': product,
            'reviews': product.reviews.all(),
            'form': ReviewForm()
        }
        return render(request, 'core/includes/review_section.html', context)
    return HttpResponse("Error in form", status=400)

@login_required
@require_POST
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user in review.likes.all():
        review.likes.remove(request.user)
    else:
        review.likes.add(request.user)
        review.dislikes.remove(request.user)
    return render(request, 'core/includes/review_actions.html', {'review': review})

@login_required
@require_POST
def dislike_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user in review.dislikes.all():
        review.dislikes.remove(request.user)
    else:
        review.dislikes.add(request.user)
        review.likes.remove(request.user)
    return render(request, 'core/includes/review_actions.html', {'review': review})


def search_box(request):
    """
    این ویو مسئول هندل کردن تمام اتفاقات سرچ باکس است.
    """
    query = request.GET.get('q', '').strip()

    # 1. حالت اول: کاربر فقط کلیک کرده و هنوز تایپ نکرده (نمایش تاریخچه + محبوب‌ها)
    if not query:
        recent_searches = []
        if request.user.is_authenticated:
            # گرفتن ۵ جستجوی آخر کاربر (تکراری‌ها رو حذف می‌کنیم)
            recent_searches = SearchHistory.objects.filter(user=request.user).values('id', 'query').distinct()[:5]

        # محبوب‌ترین جستجوها
        popular_searches = ["آیفون 13", "کفش ورزشی", "لپ تاپ ایسوس", "ساعت هوشمند"]

        return render(request, 'core/includes/search_initial.html', {
            'recent_searches': recent_searches,
            'popular_searches': popular_searches
        })

    # 2. حالت دوم: کاربر داره تایپ می‌کنه (نمایش نتایج هوشمند)

    # الف) ذخیره در تاریخچه (اگر کاربر اینتر زد یا رفت تو صفحه سرچ، اینجا فقط پیشنهاد میدیم)
    # نکته: ما اینجا ذخیره نمی‌کنیم، ذخیره رو وقتی انجام میدیم که کاربر روی نتیجه کلیک کنه یا اینتر بزنه.

    # ب) پیدا کردن دسته‌بندی‌های مرتبط
    # مثلا کاربر زده "S24" -> پیدا میکنیم کدوم دسته‌ها محصولی دارن که توش "S24" هست
    related_categories = Category.objects.filter(
        products__name__icontains=query,
        products__status=Product.Status.PUBLISHED
    ).annotate(count=Count('id')).filter(count__gt=0).distinct()[:3]

    # ج) تکمیل خودکار کلمات (Suggestions)
    # محصولاتی که نامشون با کوئری شروع میشه یا توش هست
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
    """حذف تکی تاریخچه جستجو"""
    SearchHistory.objects.filter(id=history_id, user=request.user).delete()
    return HttpResponse("")  # هیچی برنمی‌گردونه تا سطر حذف شه