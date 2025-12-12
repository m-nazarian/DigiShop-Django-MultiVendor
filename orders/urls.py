from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:product_id>/<str:action>/', views.cart_update_quantity, name='cart_update_quantity'),
    path('remove-item/<int:product_id>/', views.cart_remove_htmx, name='cart_remove_htmx'),
    path('create/', views.order_create, name='order_create'),
    path('payment/request/<int:order_id>/', views.zarinpal_payment_request, name='request_payment'),
    path('payment/verify/', views.zarinpal_payment_verify, name='verify_payment'),
]