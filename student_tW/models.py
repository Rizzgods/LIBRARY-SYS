from django.db import models
from django.contrib.auth.models import User
from librarian.models import Books
# Create your models here.

class Citations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    citation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.book.title