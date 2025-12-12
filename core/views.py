from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from products.models import Product, Review
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from products.forms import ReviewForm


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

    # محاسبه میانگین امتیاز
    reviews = product.reviews.all()
    avg_rating = 0
    if reviews.exists():
        avg_rating = sum(r.score for r in reviews) / reviews.count()

    form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'range_5': range(1, 6),
        'form': form,
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

        # بعد از ثبت، کل لیست نظرات رو دوباره میفرستیم تا آپدیت بشه
        context = {
            'product': product,
            'reviews': product.reviews.all(),
            'form': ReviewForm()  # فرم جدید و خالی
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
        review.dislikes.remove(request.user)  # اگه لایک کرد، دیس‌لایک پاک شه

    return render(request, 'core/includes/review_actions.html', {'review': review})


@login_required
@require_POST
def dislike_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.user in review.dislikes.all():
        review.dislikes.remove(request.user)
    else:
        review.dislikes.add(request.user)
        review.likes.remove(request.user)  # اگه دیس‌لایک کرد، لایک پاک شه

    return render(request, 'core/includes/review_actions.html', {'review': review})