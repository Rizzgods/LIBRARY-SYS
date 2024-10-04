import os
from django.db import models
from django.utils import timezone
from datetime import timedelta
# Create your models here.

from django.db import models
#from userauth.models import Account  # Import your custom Account model
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from student.models import Notification
from django.db.models.signals import post_save
from django.utils.timezone import now
# Create your models here.



LANGUAGE_CHOICES = [
    ('english', 'English'),
    ('filipino', 'Filipino'),
    ('spanish', 'Spanish'),
    ('other', 'Other'),
]

class Category(models.Model):
    name = models.CharField(max_length=100, default="Def")
    code = models.CharField(max_length=100, default="")
    
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Def")
    code = models.CharField(max_length=100, default="")
    def __str__(self):
        return  self.code + '-' + self.name
    
class SubSection(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Def")
    code = models.CharField(max_length=100, default="")
    def __str__(self):
        return  self.code + '-' + self.name

class Books(models.Model):
    BookTitle = models.CharField(max_length=100, unique=True)
    Author = models.CharField(max_length=100)
    Description = models.TextField(null=True, blank=True)
    Date = models.DateField()
    Category = models.ManyToManyField(Category)
    SubCategory = models.ManyToManyField(SubCategory)
    SubSection = models.ManyToManyField(SubSection)
    Language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES, default='english')
    BookFile = models.FileField(upload_to="books/files/", default='default_value.pdf')
    BookImage = models.ImageField(upload_to="books/images/", default='default_image.jpg')
    deleted_at = models.DateTimeField(null=True, blank=True)
    available = models.BooleanField(default=True)
    bookmarked_by = models.ManyToManyField(User, related_name='bookmarks', blank=True)
    borrowed = models.ManyToManyField(User, related_name='borrow', blank="True")
    PageViews = models.IntegerField(default=0)
    eBook = models.BooleanField(default=False)
    research_paper = models.BooleanField(default=False)
    hardCopy = models.BooleanField(default=False)
    stock = models.IntegerField(default=0)
    TimesBorrow = models.IntegerField(default=0)

    def __str__(self):
        return self.BookTitle
    
    def get_file_type(self):
        if self.eBook:
            return 'eBook'
        elif self.research_paper:
            return 'Research Paper'
        return 'Unknown'
    

def default_expiry():
    return timezone.now() + timedelta(days=3)

class BorrowRequest(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied'), ('Expired', 'Expired')], default='Pending')
    file_type = models.CharField(max_length=20, choices=[('eBook', 'eBook'), ('Research Paper', 'Research Paper')], default='eBook')
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    class Meta:
        indexes = [
            models.Index(fields=['book', 'requested_by']),
        ]
    


class ApprovedRequest(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField()
    approved_at = models.DateTimeField(auto_now_add=True)
    inOut = models.BooleanField(default=True)
    expireTime = models.DateTimeField(default=default_expiry)

    def __str__(self):
        return f"{self.book} approved for {self.requested_by}"
    class Meta:
        indexes = [
            models.Index(fields=['book', 'requested_by']),
        ]

class DeclinedRequest(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField()
    declined_at = models.DateTimeField(auto_now_add=True)
    decline_reason = models.CharField(max_length=255, null=True, blank=True)  # New field

    def __str__(self):
        return f"{self.book} declined for {self.requested_by}"

    class Meta:
        indexes = [
            models.Index(fields=['book', 'requested_by']),
        ]

def three_days_from_now():
    return now() + timedelta(days=3)

def get_default_user():
    return User.objects.get(pk=1)

class Out(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, default=get_default_user)
    approved_at = models.DateTimeField(auto_now_add=True)
    out = models.BooleanField(default=False)
    returnTime = models.DateTimeField(default=three_days_from_now)
    
    def __str__(self):
        return f"{self.book} status"
    
def book_returnlog_expiry():
    return now() + timedelta(days=30)    

class ReturnLog(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, default=get_default_user)
    returnLogTime = models.DateTimeField(auto_now_add=True)
    expiryLogTime = models.DateTimeField(default=book_returnlog_expiry)
    
    def __str__(self):
        return f"{self.book} status"
    
    


@receiver(post_save, sender=ApprovedRequest)
def create_approved_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.requested_by,
            message=f"Your request for {instance.book.BookTitle} has been approved.",
            notification_type='approved'  # Set notification type
        )

@receiver(post_save, sender=DeclinedRequest)
def create_declined_notification(sender, instance, created, **kwargs):
    if created:
        # Ensure the reason is included in the message and convert to title case
        decline_reason = instance.decline_reason.title() if instance.decline_reason else 'No Reason Provided'
        
        # Create the notification with the formatted reason and notification_type set to 'declined'
        Notification.objects.create(
            user=instance.requested_by,
            message=f"Your request for {instance.book.BookTitle} has been declined. Reason: {decline_reason}",
            notification_type='declined'  # Set notification type
        )