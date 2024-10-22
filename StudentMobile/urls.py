from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static 

urlpatterns = [
    path('home/', views.home, name='home'),
    path('home/book/<int:book_id>/', views.book_info, name='book_info'),
    path('home/book/<int:book_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('change_password/', views.change_password, name='change_password'),
    path('preview/<int:book_id>/', views.preview, name='preview'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)