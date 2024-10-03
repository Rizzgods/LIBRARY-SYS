from django.urls import path
from .import views
 

 
urlpatterns = [
    path('login_user/', views.login_user, name='login_user'),  # Corrected name
    path('success/', views.student_success, name='student_success'),
    path('librarian/', views.librarian_success, name='librarian_success'),
]
