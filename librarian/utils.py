from django.utils import timezone
from librarian.models import BorrowRequest, ApprovedRequest

def delete_expired_borrow_requests():
    now = timezone.now()
    expired_requests = BorrowRequest.objects.filter(expires_at__lt=now)
    count = expired_requests.count()
    expired_requests.delete()
    return count

def delete_expired_approved_requests():
    now = timezone.now()
    expired_requests = ApprovedRequest.objects.filter(expireTime__lt=now)
    count = expired_requests.count()
    expired_requests.delete()
    return count