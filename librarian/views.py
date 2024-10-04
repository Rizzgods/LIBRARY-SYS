from datetime import datetime, timedelta
import os
import time
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from .forms import BookForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import ApprovedRequest, Books, Category, LANGUAGE_CHOICES, BorrowRequest, DeclinedRequest, SubCategory, Out, ReturnLog, SubSection
from django.db.models.functions import TruncYear, ExtractYear
from librarian.utils import delete_expired_borrow_requests
from student.models import Notification



@login_required
def main(request):
    books = Books.objects.all().order_by('BookTitle').filter(available=True)
    recently_deleted_books = Books.objects.filter(deleted_at__isnull=False)
    borrow_requests = BorrowRequest.objects.filter(expires_at__gt=timezone.now())
    approved_requests = ApprovedRequest.objects.all()
    declined_requests = DeclinedRequest.objects.all()
    books_to_be_returned = Out.objects.all()
    
    book_status_approved_requests = ApprovedRequest.objects.filter(book__research_paper=False)
    book_status_books_to_be_returned = Out.objects.filter(book__research_paper=False)
    return_logs = ReturnLog.objects.all().order_by('-returnLogTime')
    language_choices = LANGUAGE_CHOICES

    years = Books.objects.annotate(year=ExtractYear('Date')).values_list('year', flat=True).distinct().order_by('-year')

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        if book_id:
            book = Books.objects.get(pk=book_id)
            book.deleted_at = timezone.now()
            book.save()
            return redirect('librarian')

    year_filter = request.GET.get('year')
    language_filter = request.GET.get('language')
    file_type_filter = request.GET.get('file_type')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')
    status_search_query = request.GET.get('status_search')
    status_reset = request.GET.get('status_reset')
    

    if year_filter:
        try:
            year = int(year_filter)
            books = books.filter(Date__year=year)
        except ValueError:
            pass

    if language_filter:
        books = books.filter(Language=language_filter)
    if file_type_filter:
        if file_type_filter == 'eBook':
            books = books.filter(eBook=True)
        elif file_type_filter == 'Research Paper':
            books = books.filter(research_paper=True)
    if category_filter:
        books = books.filter(Category__name=category_filter)
    if search_query:
        books = books.filter(BookTitle__icontains=search_query) | books.filter(Author__icontains=search_query)

    if status_search_query:
        book_status_approved_requests = book_status_approved_requests.filter(
            Q(book__BookTitle__icontains=status_search_query) |
            Q(book__Author__icontains=status_search_query)
        )
        book_status_books_to_be_returned = book_status_books_to_be_returned.filter(
            Q(book__BookTitle__icontains=status_search_query) |
            Q(book__Author__icontains=status_search_query)
        )
    if status_reset:
        return redirect('librarian')
    

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        books_data = []
        for book in books:
            books_data.append({
                'BookTitle': book.BookTitle,
                'Author': book.Author,
                'Description': book.Description,
                'Date': book.Date.strftime('%Y-%m-%d'),
                'Category': [{'name': cat.name} for cat in book.Category.all()],
                'SubCategory': [{'name': sub.name} for sub in book.SubCategory.all()],
                'Language': book.Language,
                'BookImage': book.BookImage.url if book.BookImage else None,
                'get_file_type': book.get_file_type(),
                'stock': book.stock,
                'available': book.available,
                'id': book.id
            })
        return JsonResponse({'books': books_data})

    storage = messages.get_messages(request)
    for _ in storage:
        pass  # This clears existing messages

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'The book was uploaded successfully.')
            return redirect('librarian')
        else:
            messages.error(request, 'There was an error uploading the book. Please check the form for errors and try again.')
    else:
        form = BookForm()
    
    subcategories = SubCategory.objects.all()
    categories = Category.objects.all()
    subsections = SubSection.objects.all()
    
    
    
    context = {
        'books': books,
        'recently_deleted_books': recently_deleted_books,
        'borrow_requests': borrow_requests,
        'approved_requests': approved_requests,
        'declined_requests': declined_requests,
        'books_to_be_returned': books_to_be_returned,
        'years': years,
        'language_choices': language_choices,
        'categories': categories,
        'subcategories': subcategories,
        'form': form,
        'book_status_approved_requests': book_status_approved_requests,
        'book_status_books_to_be_returned': book_status_books_to_be_returned,
        'return_logs': return_logs,
        'subsections': subsections,
    }
    return render(request, 'main.html', context)

def reset_filters(request):
    return redirect('librarian')

def edit_book(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('librarian')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'editbooks.html', {'form': form, 'book': book})


@login_required
def approve_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    ApprovedRequest.objects.create(
        book=borrow_request.book,
        requested_by=borrow_request.requested_by,
        requested_at=borrow_request.requested_at,
    )
    borrow_request.delete()
    return redirect('librarian')

def decline_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    if request.method == "POST":
        decline_reason = request.POST.get('decline_reason_input', 'No reason provided')

        # Format the reason by replacing underscores with spaces
        formatted_reason = decline_reason.replace('_', ' ')
    
        # Create a declined request with the selected reason
        DeclinedRequest.objects.create(
            book=borrow_request.book,
            requested_by=borrow_request.requested_by,
            requested_at=borrow_request.requested_at,
            decline_reason=formatted_reason  # Store formatted reason
        )
        #WAG BURAHIN INCASE
        """# Add a notification with the formatted decline reason
        Notification.objects.create(
            user=borrow_request.requested_by,
            message=f"Your request for {borrow_request.book.BookTitle} was declined. Reason: {formatted_reason}"
        ) """
        
        # Delete the original borrow request after declining it
        borrow_request.delete()
        messages.success(request, 'Request successfully declined.')
        
    return redirect('librarian')  # Redirect to your desired view
@login_required
def delete_approved_request(request, request_id):
    approved_request = get_object_or_404(ApprovedRequest, id=request_id)
    approved_request.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('librarian')))

@login_required
def delete_declined_request(request, request_id):
    declined_request = get_object_or_404(DeclinedRequest, id=request_id)
    if request.method == 'POST':
        declined_request.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('librarian')))
    else:
        pass



@login_required
def delete_book(request, book_id):
    book = Books.objects.get(pk=book_id)
    book.deleted_at = timezone.now()
    book.available = False
    book.save()
    return redirect('librarian')

@login_required
def delete_all_books(request):
    books = Books.objects.filter(deleted_at__isnull=True)
    for book in books:
        book.deleted_at = timezone.now()
        book.save()
    return redirect('librarian')

@login_required
def restore_book(request, book_id):
    book = Books.objects.get(pk=book_id)
    book.deleted_at = None
    book.available=True
    book.save()
    return redirect('librarian')    

@login_required
def delete_all_recently_deleted_books(request):
    if request.method == 'POST':
        recently_deleted_books = Books.objects.filter(deleted_at__isnull=False)
        for book in recently_deleted_books:
            if book.BookFile:
                book.BookFile.delete(save=False)
            if book.BookImage:
                book.BookImage.delete(save=False)
        recently_deleted_books.delete()
    return redirect('librarian')

def delete_recently_deleted_books(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Books, id=book_id)
        if book.BookFile:
            book.BookFile.delete(save=False)
        if book.BookImage:
            book.BookImage.delete(save=False)
        book.delete()
    return redirect('librarian')

@login_required
def toggle_availability(request, book_id):
    book = Books.objects.get(id=book_id)
    book.available = not book.available
    book.save()
    return redirect('librarian')

def logout_user(request):
    logout(request)
    messages.success(request, "You were Logged Out!")
    return redirect('login_user')

@login_required
def approve_request_view(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    ApprovedRequest.objects.create(
        book=borrow_request.book,
        requested_by=borrow_request.requested_by,
        requested_at=borrow_request.requested_at,
    )
    
    # Create a notification for the approved request
    Notification.objects.create(
        user=borrow_request.requested_by,
        message=f"Your request for {borrow_request.book.BookTitle} has been approved.",
        notification_type='approved'  # Set notification type
    )
    
    borrow_request.delete()
    return redirect('librarian')


@login_required
def decline_request_view(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    if request.method == "POST":
        decline_reason = request.POST.get('decline_reason_input', 'No reason provided')
        
        DeclinedRequest.objects.create(
            book=borrow_request.book,
            requested_by=borrow_request.requested_by,
            requested_at=borrow_request.requested_at,
            decline_reason=decline_reason
        )
        
        # Create a notification for the declined request
        Notification.objects.create(
            user=borrow_request.requested_by,
            message=f"Your request for {borrow_request.book.BookTitle} was declined. Reason: {decline_reason}",
            notification_type='declined'  # Set notification type
        )
        
        borrow_request.delete()
        messages.success(request, 'Request successfully declined.')
        
    return redirect('librarian')

@login_required
def toggle_book_status(request, request_id):
    approved_request = get_object_or_404(ApprovedRequest, id=request_id)
    approved_request.inOut = not approved_request.inOut

    if not approved_request.inOut:
        # When the book is claimed, decrease the stock and move it to the 'Out' model
        if approved_request.book.stock > 0:
            approved_request.book.stock -= 1  # Decrease stock
            approved_request.book.save()  # Save the stock update

            # Move the book to the 'Out' model
            Out.objects.create(
                book=approved_request.book,
                requested_by=approved_request.requested_by,  # Pass the correct user
                returnTime=timezone.now() + timedelta(days=14),  # Set appropriate return time
                out=True
            )

            approved_request.delete()  # Remove the approved request as it's been claimed
        else:
            messages.error(request, "Book is out of stock.")  # Optional: add a message if no stock left

    else:
        # If the book is being returned, increase the stock
        approved_request.book.stock += 1  # Increase stock when the book is returned
        approved_request.book.save()  # Save the stock update
        approved_request.save()

    return redirect(reverse('librarian'))

@login_required
def toggle_out_status(request, out_id):
    # Fetch the out record (the current borrowing entry)
    out_entry = get_object_or_404(Out, id=out_id)

    # Toggle the out status (change it to "returned")
    out_entry.out = not out_entry.out
    out_entry.save()

    if not out_entry.out:  # When the book is returned
        # Create a return log
        ReturnLog.objects.create(
            book=out_entry.book,
            requested_by=out_entry.requested_by,  # Pass the correct user who requested the book
            returnLogTime=timezone.now(),
            expiryLogTime=timezone.now() + timedelta(days=14)  # Example expiry time of 14 days from now
        )

        # Increase the stock when the book is returned
        out_entry.book.stock += 1  # Increase the stock
        out_entry.book.save()  # Save the updated stock

        # Optionally, you can delete any related approved request
        ApprovedRequest.objects.filter(book=out_entry.book, requested_by=out_entry.requested_by).delete()

        # Clean up the Out entry after processing the return
        out_entry.delete()

    return redirect(reverse('librarian'))


def book_status_view(request):
    approved_requests = ApprovedRequest.objects.select_related('book').all()
    return render(request, 'main.html', {'approved_requests': approved_requests})

def delete_expired_borrow_requests():
    expired_requests = BorrowRequest.objects.filter(expires_at__lte=timezone.now())
    expired_requests.delete()

def my_view(request):
    delete_expired_borrow_requests()
    return HttpResponse("Expired borrow requests have been deleted.")
    
def go_back(request):
    return redirect('main') 


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def keep_session_alive(request):
    request.session['last_activity'] = time.time()
    return JsonResponse({'status': 'success'})
# views.py



    