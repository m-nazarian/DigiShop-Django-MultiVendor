from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('search-box/', views.search_box, name='search_box'),
    path('remove-history/<int:history_id>/', views.remove_history, name='remove_history'),
]