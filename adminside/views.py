import csv
import io
from import_export.formats.base_formats import CSV

from django.shortcuts import render
from librarian.models import Books
from userauth.models import Account,Librarian
from django.contrib.auth.models import User
from tablib import Dataset
from .resources import AccountResource
from django.contrib import messages
# Create your views here.



import os
import csv
from django.conf import settings
from django.core.files import File
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.contrib import messages
from io import TextIOWrapper  # Add this import
from librarian.models import Books, Category, SubCategory

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










def import_csv(request):
    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if csv_file.name.endswith('.csv'):
                try:
                    # Create a resource instance
                    resource = AccountResource()

                    # Use the CSV format class to handle the file
                    file_format = CSV()
                    dataset = file_format.create_dataset(csv_file.read().decode('utf-8'))

                    # Use the resource to import the data
                    result = resource.import_data(dataset, format=file_format, raise_errors=True)

                    # Check for import errors
                    if result.has_errors():
                        messages.error(request, 'There were errors importing the CSV file.')
                    else:
                        messages.success(request, 'CSV file has been successfully imported.')
                except Exception as e:
                    messages.error(request, f'Error importing CSV file: {str(e)}')
            else:
                messages.error(request, 'Please upload a valid CSV file.')
        else:
            messages.error(request, 'No file was uploaded.')
        return redirect('book_page_views')  # Redirect to the import CSV page

    return render(request, 'import_csv.html')  # Render the form template

def adminPage(request):

   return render(request,'admin.html', {})

def your_view(request):
  return render(request,'admin.html', {})


from django.db.models import Max, Count
from django.utils import timezone


def user_is_schoolAdmin(user):
    return user.groups.filter(name='SchoolAdmin').exists()


def book_page_views(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login_user')

    # Retrieve all books and sort them by page views in descending order
    books = Books.objects.all().order_by('-PageViews')[:10]
    
    # Retrieve top eBooks sorted by times borrowed in descending order
    top_books = Books.objects.filter(eBook=True).order_by('-TimesBorrow')[:4]
    
    # Retrieve all eBooks
    ebook = Books.objects.filter(eBook=True)

    # Extract necessary data (book titles and times borrowed)
    ebook_titles = [book.BookTitle for book in ebook]
    times_borrowed = [book.TimesBorrow for book in top_books]

    # Get the most recent user activity for each user
    latest_user_activities = UserActivity.objects.filter(
        active=True
    ).values('user').annotate(
        latest_activity=Max('login_time')
    )
    
    # Retrieve the user activities corresponding to the most recent login time
    user_activities = UserActivity.objects.filter(
        active=True,
        login_time__in=[activity['latest_activity'] for activity in latest_user_activities]
    )
    
    # Calculate the count of distinct users who logged in this month
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month_start = (current_month_start + timezone.timedelta(days=31)).replace(day=1)
    distinct_users_count_this_month = UserActivity.objects.filter(
        login_time__gte=current_month_start,
        login_time__lt=next_month_start
    ).values('user').distinct().count()

    # Extract book titles and page views
    book_titles = [book.BookTitle for book in books]
    page_views = [book.PageViews for book in books]

    # Extract top eBook titles and times borrowed
    ebook_titles = [book.BookTitle for book in top_books]
    borrow = [book.TimesBorrow for book in top_books]

    # Calculate total number of students and librarians
    student_total = Account.objects.distinct().count()
    lib_total = Librarian.objects.distinct().count()
    user_total = student_total + lib_total

    # Retrieve all user logs and users
    user_logs = UserActivity.objects.all()
    users = User.objects.all()

    # Render the template with the necessary data
    return render(request, 'book_page_views.html', {
        'book_titles': book_titles, 
        'page_views': page_views, 
        'user_activities': user_activities, 
        'distinct_users_count_this_month': distinct_users_count_this_month,
        'user_total': user_total,
        'user_logs': user_logs,
        'users': users,
        'times_borrowed': times_borrowed,
        'ebook_titles': ebook_titles,
        'borrow': borrow,
    })
    # Retrieve all books and sort them by page views in descending order
    books = Books.objects.all().order_by('-PageViews')[:10]
    
    top_books = Books.objects.filter(eBook=True).order_by('-TimesBorrow')[:4]
    
    ebook = Books.objects.filter(eBook=True)

    
    # Extract necessary data (book titles and times borrowed)
    ebook_titles = [book.BookTitle for book in ebook]
    times_borrowed = [book.TimesBorrow for book in top_books]

    # Get the most recent user activity for each user
    latest_user_activities = UserActivity.objects.filter(
        active=True
    ).values('user').annotate(
        latest_activity=Max('login_time')
    )
    
    # Retrieve the user activities corresponding to the most recent login time
    user_activities = UserActivity.objects.filter(
        active=True,
        login_time__in=[activity['latest_activity'] for activity in latest_user_activities]
    )
    
    # Calculate the count of distinct users who logged in this month
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month_start = (current_month_start + timezone.timedelta(days=31)).replace(day=1)
    distinct_users_count_this_month = UserActivity.objects.filter(
        login_time__gte=current_month_start,
        login_time__lt=next_month_start
    ).values('user').distinct().count()

    # Extract book titles and page views
    book_titles = [book.BookTitle for book in books]
    page_views = [book.PageViews for book in books]

    ebook_titles = [top_books.BookTitle for top_books in top_books]
    borrow = [top_books.TimesBorrow for top_books in top_books]

    Student_total = Account.objects.distinct().count()
    lib_total = Librarian.objects.distinct().count()
    user_logs = UserActivity.objects.all()
    user_total = Student_total + lib_total
    users = User.objects.all()

    if not request.user.is_authenticated:
        return redirect('login_user')
    
    # Render the template with the necessary data
    return render(request, 'book_page_views.html', {
    'book_titles': book_titles, 
    'page_views': page_views, 
    'user_activities': user_activities, 
    'distinct_users_count_this_month': distinct_users_count_this_month,
    'user_total':user_total,
    'user_logs':user_logs,
    'users': users,  # Add this line to pass the users variable
    'times_borrowed': times_borrowed,
    'ebook_titles':ebook_titles ,
    'borrow':borrow ,
    })


# views.py

from django.shortcuts import render, redirect
from .forms import AccountForm, LibrarianForm

def create_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.save()
            return redirect('book_page_views')  # Redirect to a success page
    else:
        form = AccountForm()
    return render(request, 'book_page_views.html', {'form': form})

def create_librarian(request):
    if request.method == 'POST':
        form = LibrarianForm(request.POST)
        if form.is_valid():
            librarian = form.save(commit=False)
            librarian.save()
            return redirect('book_page_views')  # Redirect to a success page
    else:
        form = LibrarianForm()
    return render(request, 'book_page_views.html', {'form': form})






from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import UserActivity
import pytz # type: ignore

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    # Get the timezone object for Asia/Manila
    tz = pytz.timezone('Asia/Manila')
    # Get the current time in UTC
    login_time_utc = timezone.now()
    # Convert the UTC time to Philippine time
    login_time_ph = login_time_utc.astimezone(tz) + timezone.timedelta(hours=8)
    # Save the login time in the database
    UserActivity.objects.create(user=user, login_time=login_time_ph)

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    # Get the timezone object for Asia/Manila
    tz = pytz.timezone('Asia/Manila')
    # Get the current time in UTC
    logout_time_utc = timezone.now()
    # Convert the UTC time to Philippine time
    logout_time_ph = logout_time_utc.astimezone(tz) + timezone.timedelta(hours=8)
    # Retrieve the last activity for the user
    last_activity = UserActivity.objects.filter(user=user).order_by('-login_time').first()
    if last_activity:
        # Update the logout time for the last activity
        last_activity.logout_time = logout_time_ph
        last_activity.save()

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserActivity

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    # Set UserActivity instances as active upon login
    UserActivity.objects.filter(user=user, active=False).update(active=True)
    print("ACTIVE")

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    # Set UserActivity instances as inactive upon logout
    UserActivity.objects.filter(user=user, active=True).update(active=False)
    print("NOT ACTIVE")






# views.py
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

@csrf_exempt
def toggle_user_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'status': 'success', 'new_status': user.is_active})
    return JsonResponse({'status': 'error'}, status=400)


def logout_user(request):
    logout(request)
    messages.success(request, ("You were Logged Out!"))
    url = reverse('login_user')
    return redirect(url)