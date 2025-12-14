from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<str:slug>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('product/<str:slug>/add-review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/like/', views.like_review, name='like_review'),
    path('review/<int:review_id>/dislike/', views.dislike_review, name='dislike_review'),
    path('search-box/', views.search_box, name='search_box'),
    path('remove-history/<int:history_id>/', views.remove_history, name='remove_history'),
]