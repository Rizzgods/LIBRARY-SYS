from django.test import TestCase
from django.contrib.auth.models import User, Group
from .views import user_is_schoolAdmin

# test_tests.py


class UserIsSchoolAdminTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a group
        self.school_admin_group = Group.objects.create(name='schoolAdmin')

    def test_user_in_school_admin_group(self):
        # Add user to schoolAdmin group
        self.user.groups.add(self.school_admin_group)
        self.user.save()

        # Check if user is in schoolAdmin group
        self.assertTrue(user_is_schoolAdmin(self.user))

    def test_user_not_in_school_admin_group(self):
        # Ensure user is not in schoolAdmin group
        self.assertFalse(user_is_schoolAdmin(self.user))

    def test_user_with_specific_username_in_school_admin_group(self):
        # Create a user with a specific username
        specific_user = User.objects.create_user(username='cen123', password='12345')

        # Add specific user to schoolAdmin group
        specific_user.groups.add(self.school_admin_group)
        specific_user.save()

        # Check if specific user is in schoolAdmin group
        self.assertTrue(user_is_schoolAdmin(specific_user))

    def test_user_with_specific_username_not_in_school_admin_group(self):
        # Create a user with a specific username
        specific_user = User.objects.create_user(username='cen123', password='markpogi===')

        # Ensure specific user is not in schoolAdmin group
        if user_is_schoolAdmin(specific_user):
            print("cen123 is schoolAdmin")
        else:
            print("cen123 is not schoolAdmin")
        self.assertFalse(user_is_schoolAdmin(specific_user))

    def test_existing_user_in_school_admin_group(self):
        # Fetch the existing user
        existing_user = User.objects.get(username='cen123')

        # Check if existing user is in schoolAdmin group
        self.assertTrue(user_is_schoolAdmin(existing_user))