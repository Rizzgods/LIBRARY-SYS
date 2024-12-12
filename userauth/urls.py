from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetConfirmView
from django.views.generic import TemplateView 


 
urlpatterns = [
    path('login_user/', views.login_user, name='login_user'),  # Corrected name
    path('success/', views.student_success, name='student_success'),
    path('librarian/', views.librarian_success, name='librarian_success'),
    path('forgot-password/', auth_views.PasswordResetView.as_view(template_name='password-reset-form.html'), name='forgot_password'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='resetconfirmation.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/success/', TemplateView.as_view(template_name='resetsuccess.html'), name='resetsuccess'),
    path('account_request/', views.account_request, name='account_request'),
    path('account-request/success/', views.account_request_success, name='account_request_success'),

]
