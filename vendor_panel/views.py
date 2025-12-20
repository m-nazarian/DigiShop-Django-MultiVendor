from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from products.models import Product
from .forms import ProductForm
from django.contrib import messages
from accounts.models import Vendor
from orders.models import OrderItem


# 1. دکوراتور اختصاصی برای چک کردن اینکه کاربر فروشنده است
def vendor_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        # چک میکنیم آیا کاربر پروفایل vendor_profile دارد؟
        if not hasattr(request.user, 'vendor_profile'):
            return HttpResponseForbidden("شما دسترسی فروشنده ندارید.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


@vendor_required
def vendor_dashboard(request):
    """قاب اصلی پنل فروشنده"""
    return render(request, 'vendor_panel/vendor_dashboard.html')


@vendor_required
def dashboard_home(request):
    """صفحه اول داشبورد: آمار کلی"""
    vendor = request.user.vendor_profile
    products = Product.objects.filter(vendor=vendor)

    context = {
        'total_products': products.count(),
        'total_stock': sum(p.stock for p in products),
    }

    if request.htmx:
        return render(request, 'vendor_panel/partials/home.html', context)

    context['section_template'] = 'vendor_panel/partials/home.html'
    return render(request, 'vendor_panel/vendor_dashboard.html', context)


@vendor_required
def product_list(request):
    """لیست محصولات خود فروشنده"""
    vendor = request.user.vendor_profile
    products = Product.objects.filter(vendor=vendor).order_by('-created_at')

    context = {'products': products}

    if request.htmx:
        return render(request, 'vendor_panel/partials/product_list.html', context)

    context['section_template'] = 'vendor_panel/partials/product_list.html'
    return render(request, 'vendor_panel/vendor_dashboard.html', context)


@vendor_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor_profile  # اتصال خودکار به فروشنده
            product.status = Product.Status.DRAFT  # پیش‌فرض پیش‌نویس باشد تا ادمین تایید کند

            # ساخت اسلاگ خودکار
            from django.utils.text import slugify
            import time
            product.slug = slugify(product.name, allow_unicode=True) + f"-{int(time.time())}"

            product.save()
            messages.success(request, 'محصول با موفقیت ایجاد شد.')
            return redirect('vendor_panel:product_list')
    else:
        form = ProductForm()

    context = {'form': form, 'title': 'افزودن محصول جدید'}

    if request.htmx:
        return render(request, 'vendor_panel/partials/product_form.html', context)

    context['section_template'] = 'vendor_panel/partials/product_form.html'
    return render(request, 'vendor_panel/vendor_dashboard.html', context)


@vendor_required
def product_edit(request, pk):
    vendor = request.user.vendor_profile
    # فقط اجازه ویرایش محصول خود فروشنده را میدهیم
    product = get_object_or_404(Product, pk=pk, vendor=vendor)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'محصول ویرایش شد.')
            return redirect('vendor_panel:product_list')
    else:
        form = ProductForm(instance=product)

    context = {'form': form, 'title': f'ویرایش {product.name}'}

    if request.htmx:
        return render(request, 'vendor_panel/partials/product_form.html', context)

    context['section_template'] = 'vendor_panel/partials/product_form.html'
    return render(request, 'vendor_panel/vendor_dashboard.html', context)


@vendor_required
def product_delete(request, pk):
    vendor = request.user.vendor_profile
    product = get_object_or_404(Product, pk=pk, vendor=vendor)
    product.delete()
    messages.success(request, 'محصول حذف شد.')
    return redirect('vendor_panel:product_list')



@login_required
def become_vendor(request):
    # اگر کاربر قبلاً فروشنده است، بفرستش تو داشبورد
    if hasattr(request.user, 'vendor_profile'):
        return redirect('vendor_panel:dashboard')

    if request.method == 'POST':
        store_name = request.POST.get('store_name')
        description = request.POST.get('description')

        if store_name:
            if Vendor.objects.filter(store_name=store_name).exists():
                messages.error(request, 'این نام فروشگاه قبلاً ثبت شده است.')
            else:
                Vendor.objects.create(
                    user=request.user,
                    store_name=store_name,
                    description=description,
                    status=Vendor.Status.ACTIVE
                )
                messages.success(request, 'فروشگاه شما با موفقیت ساخته شد.')
                return redirect('vendor_panel:dashboard')
        else:
            messages.error(request, 'نام فروشگاه الزامی است.')

    return render(request, 'vendor_panel/become_vendor.html')


@vendor_required
def vendor_orders(request):
    vendor = request.user.vendor_profile

    # فقط آیتم‌هایی که محصولشان متعلق به این فروشنده است
    # و سفارششان پرداخت شده است
    order_items = OrderItem.objects.filter(
        product__vendor=vendor,
        order__is_paid=True
    ).select_related('order', 'product').order_by('-order__created_at')

    context = {'order_items': order_items}

    if request.htmx:
        return render(request, 'vendor_panel/partials/order_list.html', context)

    context['section_template'] = 'vendor_panel/partials/order_list.html'
    return render(request, 'vendor_panel/vendor_dashboard.html', context)


def seller_landing(request):
    """صفحه معرفی و جذب فروشندگان (لندینگ)"""
    # اگر کاربر لاگین است و قبلاً فروشنده شده، بفرستش داشبورد
    if request.user.is_authenticated and hasattr(request.user, 'vendor_profile'):
        return redirect('vendor_panel:dashboard')

    return render(request, 'vendor_panel/landing.html')