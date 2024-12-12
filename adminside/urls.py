from django.urls import path
from . import views

from django.conf import settings

from django.conf.urls.static import static 

urlpatterns = [
    path('home/', views.your_view),
    path('book-page-views/', views.book_page_views, name='book_page_views'),
    path('create-account/', views.create_account, name='create_account'),
    path('create-librarian/', views.create_librarian, name='create_librarian'),
    path('toggle_user_status/', views.toggle_user_status, name='toggle_user_status'),
    path('import-csv/', views.import_csv, name='import_csv'),
    path('batch-upload/', views.batch_upload_view, name='batch-upload'),
    path('logout/', views.logout_user, name='logout'),
    path('generate_new_password', views.generate_new_password, name='generate_new_password'),
    path('confirm_account_request/', views.confirm_account_request, name='confirm_account_request'),
    path('delete_account_request/', views.delete_account_request, name='delete_account_request'),
    ]
