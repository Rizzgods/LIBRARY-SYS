from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static 

urlpatterns = [
    path('sstudent/', views.sstudent, name='sstudent'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)