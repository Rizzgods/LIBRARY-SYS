from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from librarian.models import Books, BorrowRequest, ApprovedRequest, DeclinedRequest, LANGUAGE_CHOICES, Category
from django.urls import reverse
from django.db.models import Count, F, Q
import logging
from .models import Notification
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login_user')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'edit_pass.html', {
        'form': form,
        'user': request.user
    })



def student(request):
    filter_params = {
        'year': request.GET.get('year'),
        'category': request.GET.get('category'),
        'language': request.GET.get('language'),
        'file_type': request.GET.get('file_type')
    }

    books = Books.objects.filter(available = True, deleted_at__isnull=True)

    if filter_params['year']:
        books = books.filter(Date__year=filter_params['year'])
    if filter_params['category']:
        books = books.filter(Category__id=filter_params['category'])
    if filter_params['language']:
        books = books.filter(Language=filter_params['language'])
    if filter_params['file_type']:
        if filter_params['file_type'] == 'ebook':
            books = books.filter(eBook=True)  # Filter for ebooks
        elif filter_params['file_type'] == 'research':
            books = books.filter(research_paper=True)  # Filter for research papers

    top_viewed_books = books.order_by('-PageViews')[:7]
    categories = Category.objects.all()

    # Fetch all unique authors
    authors = Books.objects.values_list('Author', flat=True).distinct()

    # Fetch distinct years
    years = Books.objects.dates('Date', 'year').distinct()

    # Fetch research papers
    research_papers = books.filter(research_paper=True)

    # Fetch eBooks
    ebooks = books.filter(eBook=True)

    # Categorize books by category
    books_per_category = {}
    for book in books:
        for category in book.Category.all():
            if category not in books_per_category:
                books_per_category[category] = []
            books_per_category[category].append(book)

    return render(request, 'student_content.html', {
        'books': books,
        'top_viewed_books': top_viewed_books,
        'categories': categories,
        'authors': authors,
        'years': years,
        'research_papers': research_papers,
        'ebooks': ebooks,
        'filter_params': filter_params,
        'books_per_category': books_per_category,
        'language_choices': LANGUAGE_CHOICES
    })
    
def author_list(request):
    authors = Books.objects.values_list('Author', flat=True).distinct()
    return render(request, 'author_list.html', {'authors': authors})

def author_detail(request, author_name):
    # Filter books by the author's name
    author_books = Books.objects.filter(Author=author_name)
    return render(request, 'author_content.html', {'author_books': author_books, 'author_name': author_name})

def date_list(request):
    years = Books.objects.dates('Date', 'year').order_by('-Date')
    return render(request, 'date_detail.html', {'years': years})

def date_detail(request, publication_date):
    # Filter books by the publication date
    date_books = Books.objects.filter(Date__year=publication_date)
    return render(request, 'book_year_content.html', {'year_books': date_books, 'year': publication_date})

def list(request):
    years = Books.objects.dates('Date', 'year').order_by('-Date')
    return render(request, 'book_year_content.html', {'years': years})

def author_detail(request, author_name):
    # Filter books by the author's name
    author_books = Books.objects.filter(Author=author_name)
    return render(request, 'author_content.html', {'author_books': author_books, 'author': author_name})

def book_info(request, book_id):
    book = Books.objects.get(pk=book_id)
    return render(request, 'info.html', {'book': book})

def book_detail(request, book_id):
    book = get_object_or_404(Books, pk=book_id)

    borrow_requested = BorrowRequest.objects.filter(book=book, requested_by=request.user).exists()

    # Retrieve borrow_message from query parameters
    borrow_message = request.GET.get('borrow_message', "")

    context = {
        'book': book,
        'borrow_requested': borrow_requested,
        'borrow_message': borrow_message,
    }

    return render(request, 'info.html', context)




def prev_file(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    
    # Increment page views
    Books.objects.filter(pk=book_id).update(PageViews=F('PageViews') + 1)
    
    # Check if the file exists
    if not book.BookFile:
        return HttpResponseNotFound('File not found')
    
    # Bypass authentication and permission checks if the book is an eBook
    if book.eBook:
        context = {
            'book': book,
        }
        return render(request, 'prev.html', context)
    
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You need to be logged in to access this book.")
    
    # Check if there exists an approved request for the book and user
    if ApprovedRequest.objects.filter(book=book, requested_by=request.user).exists():
        context = {
            'book': book,
        }
        return render(request, 'prev.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to access this book.")

def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) >= 3:
        books = Books.objects.filter(
            (Q(BookTitle__icontains=query) | Q(Author__icontains=query)),
            deleted_at__isnull=True  # Exclude archived books
        )        
        suggestions = [
            {
                'id': book.id,
                'title': book.BookTitle,
                'author': book.Author,
                'description': book.Description,
                'date': book.Date.strftime('%Y-%m-%d'),
                'category': ', '.join(category.name for category in book.Category.all()),
                'language': book.Language,
                'image_url': book.BookImage.url,
                'views': book.PageViews,
                'available': book.available
            }
            for book in books
        ]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)

@login_required
def bookmark(request):
    # Filter books that are bookmarked by the current user
    bookmarked_books = Books.objects.filter(bookmarked_by=request.user)
    return render(request, 'bookmark_content.html', {'all_books': bookmarked_books})

@login_required
def fetch_notifications(request):
    expired_requests = BorrowRequest.objects.filter(expires_at__lt=timezone.now(), status='Pending', requested_by=request.user)
    for req in expired_requests:
        req.status = 'Expired'
        req.save()
        Notification.objects.create(
            user=req.requested_by,
            message=f"Your borrow request for {req.book.BookTitle} has expired."
        )
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = [{'id': n.id, 'message': n.message, 'read': n.read, 'created_at': n.created_at} for n in notifications]
    return JsonResponse(data, safe=False)

def mark_all_notifications_read(request):
    if request.method == 'POST':
        # Fetch all unread notifications for the current user and mark them as read
        notifications = Notification.objects.filter(user=request.user, read=False)
        notifications.update(read=True)
        return JsonResponse({'success': True})
    
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return JsonResponse({'success': True})

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return JsonResponse({'success': True})

@login_required
def bookmark_status(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    bookmarked = request.user in book.bookmarked_by.all()
    return JsonResponse({'bookmarked': bookmarked})

@login_required
def unbookmark_all(request):
    if request.method == 'POST':
        user = request.user
        try:
            user.bookmarks.clear()  # Clear the bookmarks correctly
            return JsonResponse({'success': True})
        except Exception as e:
            logging.error(f"Error unbookmarking all books for user {user.id}: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def bookmark_toggle(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        book_id = request.POST.get('book_id')
        book = get_object_or_404(Books, pk=book_id)
        user = request.user

        if user in book.bookmarked_by.all():
            book.bookmarked_by.remove(user)
            bookmarked = False
        else:
            book.bookmarked_by.add(user)
            bookmarked = True

        return JsonResponse({'bookmarked': bookmarked})
    return JsonResponse({'error': 'Invalid request'})

@login_required
def borrow_request(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    user = request.user

    borrow_requested = BorrowRequest.objects.filter(book=book, requested_by=user).exists()
    approved_requested = ApprovedRequest.objects.filter(book=book, requested_by=user).exists()

    if book.available and not borrow_requested and not approved_requested:
        # Increment the TimesBorrow field
        book.TimesBorrow += 1
        book.save()

        BorrowRequest.objects.create(book=book, requested_by=user)
        messages.success(request, "Your request to borrow this book has been submitted.")
    elif borrow_requested:
        messages.info(request, "You have already requested to borrow this book.")
    elif approved_requested:
        messages.info(request, "You have already been approved to borrow this book.")
    else:
        messages.error(request, "This book is not available for borrowing.")

    return redirect(reverse('view'))

@login_required
def request_history_view(request):
    pending_requests = BorrowRequest.objects.filter(requested_by=request.user)
    for request_obj in pending_requests:
        if request_obj.is_expired() and request_obj.status != 'Expired':
            request_obj.status = 'Expired'
            request_obj.save()

    approved_requests = ApprovedRequest.objects.filter(requested_by=request.user)
    declined_requests = DeclinedRequest.objects.filter(requested_by=request.user)

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'declined_requests': declined_requests,
    }

    return render(request, 'requesthistory.html', context)

@login_required
def borrowed_books_view(request):
    borrowed_books = ApprovedRequest.objects.filter(requested_by=request.user)

    context = {
        'borrowed_books': borrowed_books,
    }

    return render(request, 'borrowed_books.html', context)

def logout_user(request):
    logout(request)
    messages.success(request, ("You were Logged Out!"))
    url = reverse('login_user')
    return redirect (url)