from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .cart import Cart
from django.conf import settings
from .zarinpal import ZarinPal


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)

    return render(request, 'orders/includes/cart_dropdown.html', {'cart': cart})


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)

    return render(request, 'orders/includes/cart_dropdown.html', {'cart': cart})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'orders/cart_detail.html', {'cart': cart})


@require_POST
def cart_update_quantity(request, product_id, action):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # پیدا کردن تعداد فعلی در سبد
    current_quantity = cart.cart.get(str(product_id), {}).get('quantity', 0)

    if action == 'increment':
        # یکی اضافه کن
        cart.add(product=product, quantity=1)
    elif action == 'decrement':
        # یکی کم کن (اگه 1 بود و کم کرد، حذفش کن)
        if current_quantity > 1:
            cart.add(product=product, quantity=current_quantity - 1, override_quantity=True)
        else:
            cart.remove(product)

    return render(request, 'orders/includes/cart_content.html', {'cart': cart})


@require_POST
def cart_remove_htmx(request, product_id):
    """
    نسخه مخصوص حذف در صفحه سبد خرید (بدون رفرش)
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return render(request, 'orders/includes/cart_content.html', {'cart': cart})


@login_required
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # ساخت سفارش اولیه (هنوز موجودی کم نمیشه)
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()

            # انتقال آیتم‌های سبد به OrderItem
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],  # قیمت ثابت شد
                    quantity=item['quantity']
                )

            # سبد خالی میشه
            cart.clear()

            return redirect('orders:request_payment', order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})



@login_required
def zarinpal_payment_request(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    zarinpal = ZarinPal()

    # آدرس بازگشت (Callback)
    # نکته: در حالت لوکال باید 127.0.0.1 باشه نه localhost (گاهی زرین‌پال با localhost مشکل داره)
    callback_url = request.build_absolute_uri(reverse('orders:verify_payment'))

    response = zarinpal.payment_request(
        amount=order.total_price,
        description=f"پرداخت سفارش {order.id}",
        callback_url=callback_url,
        mobile=order.phone_number
    )

    if response['status']:
        # ذخیره Authority در سشن یا دیتابیس
        request.session['order_pay_authority'] = response['authority']
        request.session['order_pay_id'] = order.id
        return redirect(response['url'])  # هدایت به درگاه بانک
    else:
        return render(request, 'orders/payment_failed.html', {'error': f"خطا در اتصال به درگاه: {response['code']}"})


@login_required
@transaction.atomic
def zarinpal_payment_verify(request):
    # گرفتن پارامترهای بازگشتی از زرین‌پال
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')

    order_id = request.session.get('order_pay_id')
    order = get_object_or_404(Order, id=order_id)

    if status == 'NOK':
        return render(request, 'orders/payment_failed.html', {'error': "پرداخت توسط کاربر لغو شد یا ناموفق بود."})

    if status == 'OK':
        zarinpal = ZarinPal()
        response = zarinpal.payment_verify(order.total_price, authority)

        if response['status']:
            # --- بخش کسر موجودی (انبارداری) ---
            items = order.items.select_related('product').all()
            products_to_update = []

            try:
                for item in items:
                    product = item.product.__class__.objects.select_for_update().get(id=item.product.id)
                    if product.stock < item.quantity:
                        raise ValueError(f"موجودی کالای '{product.name}' در حین پرداخت تمام شد.")
                    product.stock -= item.quantity
                    products_to_update.append(product)

                for p in products_to_update:
                    p.save()

                # موفقیت!
                order.is_paid = True
                order.status = Order.Status.PAID
                order.transaction_id = str(response['ref_id'])  # کد پیگیری واقعی زرین پال
                order.save()

                # پاک کردن سشن‌های موقت
                del request.session['order_pay_id']
                del request.session['order_pay_authority']

                return render(request, 'orders/payment_success.html', {'order': order})

            except ValueError as e:
                return render(request, 'orders/payment_failed.html', {'error': str(e)})
        else:
            return render(request, 'orders/payment_failed.html',
                          {'error': f"تایید پرداخت ناموفق بود. کد: {response['code']}"})