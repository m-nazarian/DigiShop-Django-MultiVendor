from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from products.models import Product, Review
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from products.forms import ReviewForm

def home(request):
    products = Product.objects.filter(
        status=Product.Status.PUBLISHED,
        is_available=True
    ).select_related('category', 'brand', 'vendor').order_by('-created_at')[:12]

    context = {
        'products': products
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