from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('verify/', views.verify_otp_view, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.dashboard_overview, name='dashboard'),
    path('profile/addresses/', views.address_list, name='address_list'),
    path('profile/addresses/add/', views.address_create, name='address_create'),
    path('profile/addresses/delete/<int:pk>/', views.address_delete, name='address_delete'),
    path('profile/wishlist/', views.wishlist_view, name='wishlist'),
    path('profile/reviews/', views.user_reviews, name='user_reviews'),
]