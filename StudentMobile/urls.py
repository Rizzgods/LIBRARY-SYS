from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('home/book/<int:book_id>/', views.book_info, name='book_info'),
    path('home/book/<int:book_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('change_password/', views.change_password, name='change_password'),
]