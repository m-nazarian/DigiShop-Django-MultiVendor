from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.core.cache import cache
from django.contrib import messages
from .models import User
from .utils import send_otp_sms
import random
from .models import Address
from .forms import AddressForm
from products.models import Review


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        if phone_number:
            # 1. تولید کد تصادفی ۴ رقمی
            otp_code = random.randint(1000, 9999)

            # 2. ذخیره در کش برای 2 دقیقه (120 ثانیه)
            cache.set(f'otp_{phone_number}', otp_code, 120)

            # 3. ارسال پیامک
            sent = send_otp_sms(phone_number, otp_code)

            if sent:
                # ذخیره موبایل در سشن برای مرحله بعد
                request.session['auth_mobile'] = phone_number
                messages.success(request, 'کد تایید ارسال شد.')
                return redirect('accounts:verify_otp')
            else:
                print(f"---- TEST OTP: {otp_code} ----")
                request.session['auth_mobile'] = phone_number
                messages.warning(request, 'ارسال پیامک انجام نشد (حالت تست: کد در کنسول چاپ شد)')
                return redirect('accounts:verify_otp')
        else:
            messages.error(request, 'لطفا شماره موبایل را وارد کنید.')

    return render(request, 'accounts/login.html')


def verify_otp_view(request):
    mobile = request.session.get('auth_mobile')
    if not mobile:
        return redirect('accounts:login')

    if request.method == 'POST':
        code = request.POST.get('code')

        # خواندن کد اصلی از کش
        cached_code = cache.get(f'otp_{mobile}')

        if cached_code and str(cached_code) == code:
            # کد صحیح است!

            # کاربر را پیدا کن یا بساز (Get or Create)
            user, created = User.objects.get_or_create(phone_number=mobile)

            # لاگین کردن کاربر
            login(request, user)

            # پاک کردن سشن و کش
            del request.session['auth_mobile']
            cache.delete(f'otp_{mobile}')

            messages.success(request, 'خوش آمدید!')
            return redirect('core:home')
        else:
            messages.error(request, 'کد وارد شده اشتباه یا منقضی شده است.')

    return render(request, 'accounts/verify.html', {'mobile': mobile})


def logout_view(request):
    logout(request)
    messages.info(request, 'با موفقیت خارج شدید.')
    return redirect('core:home')



@login_required
def dashboard_overview(request):
    """صفحه اصلی داشبورد: نمایش آخرین سفارش‌ها و وضعیت کلی"""
    recent_orders = request.user.orders.all()[:5]
    return render(request, 'accounts/dashboard/overview.html', {'recent_orders': recent_orders})

@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/dashboard/address_list.html', {'addresses': addresses})

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