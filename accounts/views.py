from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.core.cache import cache
from django.contrib import messages

from products.models import Review
from .utils import send_otp_sms
import random
from .models import Address
from .forms import AddressForm, UserEditForm  # ✅ اضافه شدن فرم جدید
from orders.models import Order

User = get_user_model()


# --- بخش لاگین و احراز هویت (بدون تغییر) ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if phone_number:
            otp_code = random.randint(1000, 9999)
            cache.set(f'otp_{phone_number}', otp_code, 120)
            print(f"---- TEST OTP: {otp_code} ----")  # برای تست
            send_otp_sms(phone_number, otp_code)
            request.session['auth_mobile'] = phone_number
            messages.success(request, 'کد تایید ارسال شد.')
            return redirect('accounts:verify_otp')
        else:
            messages.error(request, 'لطفا شماره موبایل را وارد کنید.')
    return render(request, 'accounts/login.html')


def verify_otp_view(request):
    mobile = request.session.get('auth_mobile')
    if not mobile: return redirect('accounts:login')
    if request.method == 'POST':
        code = request.POST.get('code')
        cached_code = cache.get(f'otp_{mobile}')
        if cached_code and str(cached_code) == code:
            user, created = User.objects.get_or_create(phone_number=mobile)
            login(request, user)
            del request.session['auth_mobile']
            cache.delete(f'otp_{mobile}')
            messages.success(request, 'خوش آمدید!')
            return redirect('core:home')
        else:
            messages.error(request, 'کد اشتباه است.')
    return render(request, 'accounts/verify.html', {'mobile': mobile})


def logout_view(request):
    logout(request)
    messages.info(request, 'خارج شدید.')
    return redirect('core:home')


# --- بخش داشبورد SPA (جدید) ---

@login_required
def dashboard(request):
    """صفحه اصلی داشبورد (خالی)"""
    # این ویو فقط وقتی اجرا میشه که کاربر بزنه /dashboard/
    return render(request, 'accounts/dashboard.html')


@login_required
def dashboard_summary(request):
    orders = request.user.orders.all().order_by('-created_at')
    context = {
        'recent_orders': orders[:5],
        'processing_count': orders.filter(status='processing').count(),
        'delivered_count': orders.filter(status='delivered').count(),
        'favorites_count': request.user.wishlist.count(),
    }

    # ✅ اگر درخواست HTMX بود (کلیک روی سایدبار)
    if request.htmx:
        return render(request, 'accounts/partials/summary.html', context)

    # ✅ اگر رفرش کرد (نمایش قالب کامل + تزریق محتوا)
    context['section_template'] = 'accounts/partials/summary.html'
    return render(request, 'accounts/dashboard.html', context)


@login_required
def dashboard_orders(request):
    status_filter = request.GET.get('status')
    orders = request.user.orders.all().order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {'orders': orders}

    if request.htmx:
        return render(request, 'accounts/partials/orders_list.html', context)

    context['section_template'] = 'accounts/partials/orders_list.html'
    return render(request, 'accounts/dashboard.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات پروفایل با موفقیت بروز شد.')
            return render(request, 'accounts/partials/edit_profile.html', {'form': form})
    else:
        form = UserEditForm(instance=request.user)

    context = {'form': form}

    if request.htmx:
        return render(request, 'accounts/partials/edit_profile.html', context)

    context['section_template'] = 'accounts/partials/edit_profile.html'
    return render(request, 'accounts/dashboard.html', context)


@login_required
def dashboard_favorites(request):
    products = request.user.wishlist.all()
    context = {'products': products}

    if request.htmx:
        return render(request, 'accounts/partials/favorites.html', context)

    context['section_template'] = 'accounts/partials/favorites.html'
    return render(request, 'accounts/dashboard.html', context)


@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    context = {'addresses': addresses}

    if request.htmx:
        return render(request, 'accounts/partials/address_list.html', context)

    context['section_template'] = 'accounts/partials/address_list.html'
    return render(request, 'accounts/dashboard.html', context)


@login_required
def address_create(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'آدرس جدید با موفقیت ثبت شد.')
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    return render(request, 'accounts/dashboard/address_form.html', {'form': form})

@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'آدرس حذف شد.')
    return redirect('accounts:address_list')


@login_required
def wishlist_view(request):
    products = request.user.wishlist.all()
    return render(request, 'accounts/dashboard/wishlist.html', {'products': products})

@login_required
def user_reviews(request):
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'accounts/dashboard/user_reviews.html', {'reviews': reviews})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}

    if request.htmx:
        return render(request, 'accounts/partials/order_detail.html', context)

    context['section_template'] = 'accounts/partials/order_detail.html'
    return render(request, 'accounts/dashboard.html', context)