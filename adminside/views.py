from django.shortcuts import render
from librarian.models import Books
from userauth.models import Account,Librarian
from django.contrib.auth.models import User
# Create your views here.
def adminPage(request):

   return render(request,'admin.html', {})

def your_view(request):
    # Fetch all UserActivity instances
    user_activities = UserActivity.objects.all()

    # Print the contents of user_activities in the console
    for activity in user_activities:
        print(activity.user.username, activity.login_time, activity.logout_time, activity.active)
    else:
        print("nothing")
    # Pass user_activities to template context
    context = {
        'user_activities': user_activities
    }
    return render(request, 'book_page_views.html', context)



from django.db.models import Max, Count
from django.utils import timezone

def book_page_views(request):
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

@csrf_exempt
def toggle_user_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'status': 'success', 'new_status': user.is_active})
    return JsonResponse({'status': 'error'}, status=400)


