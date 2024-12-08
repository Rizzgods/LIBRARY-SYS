from django.contrib.auth.models import Group
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Account(models.Model):
    lrn = models.CharField(max_length=12, unique=True)
    fname = models.CharField(max_length=50, verbose_name="First Name")
    lname = models.CharField(max_length=50, verbose_name="Last Name")
    address = models.CharField(max_length=50)
    birthday = models.DateField()
    age = models.IntegerField()
    email = models.EmailField(max_length=50, verbose_name="Email")

    def __str__(self):
        return self.lrn + ' ' + str(self.birthday)


@receiver(post_save, sender=Account)
def create_user_and_assign_group(sender, instance, created, **kwargs):
    if created:
        # Create the user account
        user = User.objects.create_user(
            username=instance.lrn,
            email=instance.email,
            password=str(instance.birthday),
            first_name=instance.fname,
            last_name=instance.lname
        )
        # Assign user to a group
        student_group, _ = Group.objects.get_or_create(name='Student')
        user.groups.add(student_group)


class Librarian(models.Model):
    Username = models.CharField(max_length=50)
    fname = models.CharField(max_length=50, verbose_name="First Name", default="")
    lname = models.CharField(max_length=50, verbose_name="Last Name", default="")
    email = models.EmailField(max_length=50, verbose_name="Email", default="")
    Bday = models.DateField()

@receiver(post_save, sender=Librarian)
def create_librarian_user_and_assign_group(sender, instance, created, **kwargs):
    if created:
        # Create the user account
        user = User.objects.create_user(
            username=instance.Username,
            email=instance.email,
            password=str(instance.Bday),
            first_name=instance.fname,
            last_name=instance.lname
        )
        # Assign user to a group
        librarian_group, _ = Group.objects.get_or_create(name='Librarian')
        user.groups.add(librarian_group)