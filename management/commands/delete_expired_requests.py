from django.core.management.base import BaseCommand
from django.utils import timezone
from librarian.models import BorrowRequest
from librarian.utils import delete_expired_borrow_requests

class Command(BaseCommand):
    help = 'Delete expired borrow requests'

    def handle(self, *args, **kwargs):
        count = delete_expired_borrow_requests()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired borrow requests'))
