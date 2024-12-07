from datetime import datetime, timedelta
import os
import time
import json
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect,HttpResponseNotAllowed
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
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from userauth.models import Account  # Ensure these models are imported
from django.core.mail import EmailMessage

@login_required
def main(request):
    # Initial Queries
    books = Books.objects.all().order_by('BookTitle').filter(available=True)
    recently_deleted_books = Books.objects.filter(deleted_at__isnull=False)
    borrow_requests = BorrowRequest.objects.filter(expires_at__gt=timezone.now())
    approved_requests = ApprovedRequest.objects.all()
    declined_requests = DeclinedRequest.objects.all()
    books_to_be_returned = Out.objects.all()
    
    # Homepage Statistics
    total_books = books.count()
    pending_borrow_requests = BorrowRequest.objects.filter(expires_at__gt=timezone.now()).count()
    current_date = timezone.now()
    start_of_month = current_date.replace(day=1)
    books_added_this_month = Books.objects.filter(Date__gte=start_of_month).count()
    recently_deleted_books_count = Books.objects.filter(deleted_at__isnull=False).count()

    # Book Status Queries
    book_status_approved_requests = ApprovedRequest.objects.filter(book__research_paper=False)
    book_status_books_to_be_returned = Out.objects.filter(book__research_paper=False)
    return_logs = ReturnLog.objects.all().order_by('-returnLogTime')
    language_choices = LANGUAGE_CHOICES
    years = Books.objects.annotate(year=ExtractYear('Date')).values_list('year', flat=True).distinct().order_by('-year')

    # Handle POST request for book deletion
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        if book_id:
            book = Books.objects.get(pk=book_id)
            book.deleted_at = timezone.now()
            book.save()
            return redirect('librarian')

    # Handle form submission for new book
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                book = form.save(commit=False)
                
                # Handle author data
                authors_json = request.POST.get('authors')
                if authors_json:
                    authors_list = json.loads(authors_json)
                    book.Author = ', '.join(authors_list)
                
                book.save()
                form.save_m2m()  # Save many-to-many relationships
                
                messages.success(request, 'The book was uploaded successfully.')
                return redirect('librarian')
            except Exception as e:
                messages.error(request, f'Error saving book: {str(e)}')
        else:
            messages.error(request, 'There was an error uploading the book. Please check the form for errors and try again.')
    else:
        form = BookForm()

    # Handle Filters
    year_filter = request.GET.get('year')
    language_filter = request.GET.get('language')
    file_type_filter = request.GET.get('file_type')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')
    status_search_query = request.GET.get('status_search')
    status_reset = request.GET.get('status_reset')

    # Apply Filters
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
        books = books.filter(
            Q(BookTitle__icontains=search_query) |
            Q(Author__icontains=search_query)
        )

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

    # Handle AJAX requests
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

    # Clear existing messages
    storage = messages.get_messages(request)
    for _ in storage:
        pass

    # Get additional data for template
    subcategories = SubCategory.objects.all()
    categories = Category.objects.all()
    subsections = SubSection.objects.all()

    # Prepare context for template
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
        'total_books': total_books,
        'pending_borrow_requests': pending_borrow_requests,
        'books_added_this_month': books_added_this_month,
        'recently_deleted_books_count': recently_deleted_books_count,
    }

    return render(request, 'main.html', context)

def batch_upload_view(request):
    if not request.user.is_authenticated or not user_is_schoolAdmin(request.user):
        return redirect('login_user')

    if request.method == 'POST':
        csv_file = request.FILES.get('csvFile')
        files = request.FILES.getlist('fileFolder')

        if not csv_file or not files:
            messages.error(request, "Please upload both a CSV file and a folder with files.")
            return redirect('your_upload_view_url')

        # Save the uploaded folder files temporarily
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        for f in files:
            file_path = os.path.join(temp_dir, f.name)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

        # Process the CSV file
        try:
            # Handle the CSV file, wrapped in a TextIOWrapper to ensure it's read as text
            csv_file = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                book = Books(
                    BookTitle=row['BookTitle'],
                    Author=row['Author'],
                    Description=row.get('Description', ''),
                    Date=row['Date'],
                    Language=row['Language'],
                    eBook=row['eBook'].lower() == 'true',
                    research_paper=row['research_paper'].lower() == 'true',
                    hardCopy=row['hardCopy'].lower() == 'true',
                    stock=int(row['stock']),
                )
                book.save()

                # Link categories and subcategories
                categories = Category.objects.filter(id__in=row['Category'].split(','))
                book.Category.add(*categories)

                subcategories = SubCategory.objects.filter(id__in=row['SubCategory'].split(','))
                book.SubCategory.add(*subcategories)

                # Link the uploaded files by matching filenames
                book_file_path = os.path.join(temp_dir, row['BookFile'])
                book_image_path = os.path.join(temp_dir, row['BookImage'])

                if os.path.exists(book_file_path):
                    with open(book_file_path, 'rb') as bf:
                        book.BookFile.save(row['BookFile'], File(bf), save=False)

                if os.path.exists(book_image_path):
                    with open(book_image_path, 'rb') as bi:
                        book.BookImage.save(row['BookImage'], File(bi), save=False)

                book.save()

            messages.success(request, "Books uploaded successfully!")
        except Exception as e:
            messages.error(request, f"Error processing the upload: {e}")
        finally:
            # Clean up temporary files
            for f in files:
                file_path = os.path.join(temp_dir, f.name)
                if os.path.exists(file_path):
                    os.remove(file_path)

            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

        return redirect('batch-upload')

    return render(request, 'admin.html')

def reset_filters(request):
    return redirect('librarian')

def get_subcategories(request, category_id):
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse({'subcategories': list(subcategories)})

def get_subsections(request, subcategory_id):
    subsections = SubSection.objects.filter(sub_category_id=subcategory_id).values('id', 'name')
    return JsonResponse({'subsections': list(subsections)})

def edit_book(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    categories = Category.objects.all()
    
    # Fetch subcategories and subsections based on the current book's categories
    subcategories = SubCategory.objects.filter(category__in=book.Category.all())
    subsections = SubSection.objects.filter(sub_category__in=book.SubCategory.all())

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)

            # Check if a new image is uploaded
            if 'BookImage' in request.FILES:
                book.BookImage = request.FILES['BookImage']

            # Save the book instance
            book.save()

            # Update the many-to-many relationships
            form.save_m2m()  # This saves the many-to-many relationships

            messages.success(request, 'Book updated successfully!')
            return redirect('librarian')  # Redirect to the list of books or another appropriate page
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = BookForm(instance=book)

    context = {
        'form': form,
        'book': book,
        'categories': categories,
        'subcategories': subcategories,
        'subsections': subsections,
    }
    return render(request, 'editbooks.html', context)

@login_required
def approve_request(request, request_id):
    if request.method == 'POST':
        try:
            borrow_request = get_object_or_404(BorrowRequest, id=request_id)
            
            # Create ApprovedRequest
            ApprovedRequest.objects.create(
                book=borrow_request.book,
                requested_by=borrow_request.requested_by,
                requested_at=borrow_request.requested_at,
            )

            # Send approval email
            email_response = send_approval_email(request, request_id)
            if email_response.status_code != 200:
                return JsonResponse({'status': 'error', 'message': 'Failed to send approval email.'}, status=500)

            # Create notification if it doesn't exist
            message = f"Your request for {borrow_request.book.BookTitle} has been approved."
            notification_exists = Notification.objects.filter(
                user=borrow_request.requested_by,
                message=message,
                notification_type='approved'
            ).exists()

            if not notification_exists:
                Notification.objects.create(
                    user=borrow_request.requested_by,
                    message=message,
                    notification_type='approved'
                )

            # Delete borrow request
            borrow_request.delete()

            return JsonResponse({'status': 'success', 'message': 'Request approved successfully!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)  

def decline_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    if request.method == "POST":
        decline_reason = request.POST.get('decline_reason_input', 'No reason provided')
        formatted_reason = decline_reason.replace('_', ' ')
    
        # Create a declined request with the selected reason
        DeclinedRequest.objects.create(
            book=borrow_request.book,
            requested_by=borrow_request.requested_by,
            requested_at=borrow_request.requested_at,
            decline_reason=formatted_reason
        )

        # Delete the original borrow request
        borrow_request.delete()

        messages.success(request, 'Request successfully declined.')
        
    # Redirect to the borrow requests section (borrow-req tab)
    return redirect(reverse('librarian') + '#borrow-req')
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
    # Allow only POST requests
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Retrieve the book instance or return 404 if not found
    book = get_object_or_404(Books, id=book_id)

    # Delete files if they exist
    if book.BookFile:
        book.BookFile.delete(save=False)
    if book.BookImage:
        book.BookImage.delete(save=False)

    # Delete the book record
    book.delete()

    # Redirect to the librarian view after deletion
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


@require_POST
def decline_request_view(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    decline_reason = request.POST.get('decline_reason_input', 'Other')

    # Create DeclinedRequest with the captured decline reason
    declined_request = DeclinedRequest.objects.create(
        book=borrow_request.book,
        requested_by=borrow_request.requested_by,
        requested_at=borrow_request.requested_at,
        decline_reason=decline_reason
    )
    # Delete the original borrow request if required
    borrow_request.delete()

    return redirect('librarian')  # Or wherever you want to redirect


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


@login_required
def borrow_request_view(request):
    # Fetch pending requests, ordered by the 'requested_at' field in descending order
    pending_requests = BorrowRequest.objects.filter(requested_by=request.user).order_by('-requested_at')
    
    # Fetch approved requests, ordered by the 'approved_at' field in descending order
    approved_requests = ApprovedRequest.objects.filter(requested_by=request.user).order_by('-approved_at')
    
    # Fetch declined requests, ordered by the 'declined_at' field in descending order
    declined_requests = DeclinedRequest.objects.filter(requested_by=request.user).order_by('-declined_at')

    # Handle expired requests in pending requests
    for pending_request in pending_requests:
        if pending_request.is_expired() and pending_request.status != 'Expired':
            pending_request.status = 'Expired'
            pending_request.save()

    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'declined_requests': declined_requests,
    }

    return render(request, 'borrow_request_table.html', context)




from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def keep_session_alive(request):
    request.session['last_activity'] = time.time()
    return JsonResponse({'status': 'success'})
# views.py



from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BorrowRequest, ApprovedRequest, DeclinedRequest
from .serializers import BorrowRequestSerializer, ApprovedRequestSerializer, DeclinedRequestSerializer

@api_view(['GET'])
def get_borrow_requests(request):
    borrow_requests = BorrowRequest.objects.all()
    approved_requests = ApprovedRequest.objects.all()
    declined_requests = DeclinedRequest.objects.all()
    
    borrow_requests_serializer = BorrowRequestSerializer(borrow_requests, many=True)
    approved_requests_serializer = ApprovedRequestSerializer(approved_requests, many=True)
    declined_requests_serializer = DeclinedRequestSerializer(declined_requests, many=True)
    
    return Response({
        'borrow_requests': borrow_requests_serializer.data,
        'approved_requests': approved_requests_serializer.data,
        'declined_requests': declined_requests_serializer.data,
    })

@csrf_exempt  # Be cautious using this in production
def send_reminder(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        book_title = data.get('book_title')
        user_id = data.get('user_id')

        try:
            # Retrieve the User instance
            user = User.objects.get(id=user_id)
            # Retrieve the Account instance using the user instance
            account = Account.objects.get(user=user)  # This should work if the relationship is correct

            user_email = account.email  # Get the email from the Account model

            # Create a notification
            Notification.objects.create(
                user=account.user,
                message=f"Reminder: The book '{book_title}' is due for return.",
                notification_type='reminder'
            )

            # Email subject
            subject = 'Reminder: Book Due Soon'
            from_email = 'lawangbatolibrary@gmail.com'  # Replace with your actual email

            # HTML email content
            html_message = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Reminder: Book Due Soon</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    .email-container {{
                        width: 100%;
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    }}
                    .email-header {{
                        background-color: #3E91CA; /* Updated to match the new color */
                        padding: 20px;
                        text-align: center;
                        color: #ffffff;
                    }}
                    .email-header img {{
                        width: 150px;
                        margin-bottom: 10px;
                    }}
                    .email-header h1 {{
                        margin: 0;
                        font-size: 24px;
                    }}
                    .email-body {{
                        padding: 20px;
                    }}
                    .email-body h2 {{
                        color: #333;
                        font-size: 22px;
                    }}
                    .email-body p {{
                        font-size: 16px;
                        color: #555;
                        line-height: 1.6;
                    }}
                    .email-body .button {{
                        background-color: #38b6ff;  /* Button color matching logo */
                        color: #fff;
                        text-decoration: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        display: inline-block;
                        margin-top: 20px;
                    }}
                    .email-footer {{
                        background-color: #3E91CA;/* Also applied the color to the footer */
                        color: #ffffff;
                        text-align: center;
                        padding: 10px;
                        font-size: 14px;
                    }}
                    .email-footer p {{
                        margin: 0;
                    }}
                    .email-footer .disclaimer {{
                        font-size: 12px;
                        color: #f1f1f1;
                    }}
                </style>
            </head>
            <body>

            <div class="email-container">
                <div class="email-header">
                    <img src="http://127.0.0.1:8000/static/playground/NewLogo.png" alt="LBLIB Logo"> <!-- Adjust URL for local -->
                    <h1>LBLIB - Your Library at Your Fingertips</h1>
                </div>
                <div class="email-body">
                    <h2>Reminder: Book Due Soon</h2>
                    <p>This is a reminder that the book <strong>"{book_title}"</strong> is due soon.</p>
                    <p>Please return the book at your earliest convenience.</p>
                    <p>This is an automated email. Please do not reply to this message. For further inquiries, contact us through the appropriate channels.</p>
                    <a href="http://your-library-url.com/borrow" class="button">View Borrow Details</a>
                </div>
                <div class="email-footer">
                    <p>Thank you for using LBLIB - Your Library at Your Fingertips!</p>
                    <p class="disclaimer">Property of Lawang Bato.</p> <!-- Changed disclaimer here -->
                </div>
            </div>

            </body>
            </html>
            """

            # Send the email with HTML content
            email = EmailMessage(
                subject,
                html_message,
                from_email,
                [user_email],
            )
            email.content_subtype = 'html'  # This tells the email that it contains HTML content
            email.send(fail_silently=False)

            return JsonResponse({'status': 'success', 'message': 'Reminder sent and email notification sent successfully!'})

        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except Account.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Account not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@csrf_exempt  # Be cautious using this in production
def send_approval_email(request, request_id):
    if request.method == 'POST':
        try:
            # Ensure the request_id is provided
            if not request_id:
                return JsonResponse({'status': 'error', 'message': 'Request ID is required.'}, status=400)

            # Get the BorrowRequest and User information
            borrow_request = BorrowRequest.objects.get(id=request_id)
            user = borrow_request.requested_by
            account = Account.objects.get(user=user)

            user_email = account.email  # Get the email from the Account model

            # Email subject
            subject = 'Your Borrow Request Has Been Approved'
            from_email = 'lawangbatolibrary@gmail.com'  # Replace with your actual email

            # HTML email content
            html_message = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Your Borrow Request Has Been Approved</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    .email-container {{
                        width: 100%;
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    }}
                    .email-header {{
                        background-color: #3E91CA; /* Updated to match the new color */
                        padding: 20px;
                        text-align: center;
                        color: #ffffff;
                    }}
                    .email-header img {{
                        width: 150px;
                        margin-bottom: 10px;
                    }}
                    .email-header h1 {{
                        margin: 0;
                        font-size: 24px;
                    }}
                    .email-body {{
                        padding: 20px;
                    }}
                    .email-body h2 {{
                        color: #333;
                        font-size: 22px;
                    }}
                    .email-body p {{
                        font-size: 16px;
                        color: #555;
                        line-height: 1.6;
                    }}
                    .email-body .button {{
                        background-color: #38b6ff;  /* Button color matching logo */
                        color: #fff;
                        text-decoration: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        display: inline-block;
                        margin-top: 20px;
                    }}
                    .email-footer {{
                        background-color: #3E91CA;/* Also applied the color to the footer */
                        color: #ffffff;
                        text-align: center;
                        padding: 10px;
                        font-size: 14px;
                    }}
                    .email-footer p {{
                        margin: 0;
                    }}
                    .email-footer .disclaimer {{
                        font-size: 12px;
                        color: #f1f1f1;
                    }}
                </style>
            </head>
            <body>

            <div class="email-container">
                <div class="email-header">
                    <img src="http://127.0.0.1:8000/static/playground/NewLogo.png" alt="LBLIB Logo"> <!-- Adjust URL for local -->
                    <h1>LBLIB - Your Library at Your Fingertips</h1>
                </div>
                <div class="email-body">
                    <h2>Congratulations!</h2>
                    <p>Your borrow request for the book <strong>"{borrow_request.book.BookTitle}"</strong> has been approved.</p>
                    <p>We are happy to let you know that your request is now processed, and the book will be ready for you to pick up at the specified time. We hope you enjoy reading it!</p>
                    <p>This is an automated email. Please do not reply to this message. If you have any questions, feel free to contact us through the proper channels.</p>
                    <a href="http://your-library-url.com/borrow" class="button">View Borrow Details</a>
                </div>
                <div class="email-footer">
                    <p>Thank you for using LBLIB - Your Library at Your Fingertips!</p>
                    <p class="disclaimer">Property of Lawang Bato.</p> <!-- Changed disclaimer here -->
                </div>
            </div>

            </body>
            </html>
            """

            # Send the email with HTML content
            email = EmailMessage(
                subject,
                html_message,
                from_email,
                [user_email],
            )
            email.content_subtype = 'html'  # This tells the email that it contains HTML content
            email.send(fail_silently=False)

            return JsonResponse({'status': 'success', 'message': 'Approval email sent successfully!'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
        except BorrowRequest.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Borrow request not found.'}, status=404)
        except Account.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Account not found for the user.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
