from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('verify/', views.verify_otp_view, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),

    # URL اصلی داشبورد
    path('dashboard/', views.dashboard, name='dashboard'),

    # URL های پارشیال (برای HTMX)
    path('dashboard/summary/', views.dashboard_summary, name='dashboard_summary'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/edit-profile/', views.edit_profile, name='edit_profile'),  # ✅ جدید
    path('dashboard/favorites/', views.dashboard_favorites, name='dashboard_favorites'),
    path('dashboard/addresses/', views.address_list, name='address_list'),
    path('dashboard/orders/<int:order_id>/', views.order_detail, name='order_detail'),


]