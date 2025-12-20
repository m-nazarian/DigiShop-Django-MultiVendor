from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('api/category-attributes/<int:category_id>/', views.get_category_attributes, name='category_attributes'),
    path('', views.product_list, name='product_list'),
    path('amazing-offers/', views.amazing_offers, name='amazing_offers'),

    path('compare/', views.compare_products, name='compare_products'),
    path('compare/search/', views.search_for_compare, name='search_for_compare'),
    path('compare/add/<int:product_id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/remove/<int:product_id>/', views.remove_from_compare, name='remove_from_compare'),

    path('wishlist/toggle/<str:slug>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('reviews/add/<str:slug>/', views.add_review, name='add_review'),
    path('reviews/like/<int:review_id>/', views.like_review, name='like_review'),
    path('reviews/dislike/<int:review_id>/', views.dislike_review, name='dislike_review'),

    path('<str:slug>/', views.product_detail, name='product_detail'),
]