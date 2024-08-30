from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('student/', views.student, name="view"),
    path('preview/<int:book_id>/', views.prev_file, name='prev_file'),
    path('book-detail/<int:book_id>/', views.book_detail, name='book_detail'),
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('bookmark/', views.bookmark, name='bookmark'),
    path('bookmark_toggle/', views.bookmark_toggle, name='bookmark_toggle'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('author/<str:author_name>/', views.author_detail, name='author_detail'),
    path('date/<int:publication_date>/', views.date_detail, name='date_detail'),
    path('list/<int:year>/', views.list, name='list'),
    path('author_list/', views.author_list, name='author_list'),
    path('author_detail/<str:author_name>/', views.author_detail, name='author_detail'),
    path('date/', views.date_list, name='date_list'),
    path('borrow-request/<int:book_id>/', views.borrow_request, name='borrow_request'),
    path('student/book-detail/<int:book_id>/', views.book_detail, name='book_detail'),
    path('request-history/', views.request_history_view, name='request_history'),
    path('bookmark_status/<int:book_id>/', views.bookmark_status, name='bookmark_status'),
    path('unbookmark_all/', views.unbookmark_all, name='unbookmark_all'),
    path('notifications/', views.fetch_notifications, name='fetch_notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('borrowed-books/', views.borrowed_books_view, name='borrowed_books'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)