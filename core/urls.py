from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<str:slug>/', views.product_detail, name='product_detail'),
    path('product/<str:slug>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
]