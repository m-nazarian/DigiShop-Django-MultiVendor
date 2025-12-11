from django.shortcuts import render, get_object_or_404
from products.models import Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def home(request):
    # فقط محصولات منتشر شده و موجود رو بیار
    # جدیدترین‌ها اول باشن
    products = Product.objects.filter(
        status=Product.Status.PUBLISHED,
        is_available=True
    ).select_related('category', 'brand', 'vendor').order_by('-created_at')[:12] # فعلا ۱۲ تا

    context = {
        'products': products
    }
    return render(request, 'core/home.html', context)



def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('vendor', 'category', 'brand').prefetch_related('images', 'reviews__user'),
        slug=slug,
        status=Product.Status.PUBLISHED
    )

    # محاسبه میانگین امتیاز (ساده) - بعدا دقیق‌ترش می‌کنیم
    reviews = product.reviews.all()
    avg_rating = 0
    if reviews.exists():
        avg_rating = sum(r.score for r in reviews) / reviews.count()

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'range_5': range(1, 6),
    }
    return render(request, 'core/product_detail.html', context)


@login_required
@require_POST
def toggle_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if product.wishlist.filter(id=request.user.id).exists():
        product.wishlist.remove(request.user)  # حذف از علاقه مندی
    else:
        product.wishlist.add(request.user)  # افزودن به علاقه مندی

    # فقط دکمه جدید رو برمی‌گردونیم، نه کل صفحه رو!
    return render(request, 'core/includes/wishlist_button.html', {'product': product})