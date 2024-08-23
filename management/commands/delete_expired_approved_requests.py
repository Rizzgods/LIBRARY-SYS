from django.core.management.base import BaseCommand
from django.utils import timezone
from librarian.utils import delete_expired_approved_requests

class Command(BaseCommand):
    help = 'Delete expired approved requests'

    def handle(self, *args, **kwargs):
        count = delete_expired_approved_requests()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired approved requests'))
