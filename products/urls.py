from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('api/category-attributes/<int:category_id>/', views.get_category_attributes, name='category_attributes'),
    path('', views.product_list, name='product_list'),
    path('<str:slug>/', views.product_detail, name='product_detail'),
]