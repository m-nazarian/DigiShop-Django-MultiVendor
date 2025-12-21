from django.urls import path
from . import views

app_name = 'vendor_panel'

urlpatterns = [
    path('start-selling/', views.seller_landing, name='seller_landing'),
    path('', views.dashboard_home, name='dashboard'),
    path('register/', views.become_vendor, name='become_vendor'),
    path('orders/', views.vendor_orders, name='vendor_orders'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
]