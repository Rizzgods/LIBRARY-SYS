from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

# Define user check functions
def user_is_student(user):
    return user.groups.filter(name='Student').exists()

def user_is_librarian(user):
    return user.groups.filter(name='Librarian').exists()

def user_is_schoolAdmin(user):
    return user.groups.filter(name='SchoolAdmin').exists()

# Define views
@login_required(login_url='login_user')
@user_passes_test(user_is_student, login_url='login_user')
def student_success(request):
    url = reverse('view')  # Replace 'student_dashboard' with the URL name for the student dashboard
    return redirect(url)

@login_required(login_url='login_user')
@user_passes_test(user_is_librarian, login_url='login_user')
def librarian_success(request):
    url = reverse('librarian')  # Replace 'librarian_dashboard' with the URL name for the librarian dashboard
    return redirect(url)

@login_required(login_url='login_user')
@user_passes_test(user_is_schoolAdmin, login_url='login_user')
def schoolAdmin_success(request):
    url = reverse('book_page_views')  # Redirect to the correct URL for SchoolAdmin
    return redirect(url)

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Debugging: Check the groups of the user
                user_groups = user.groups.all()
                print(f"User Groups: {[group.name for group in user_groups]}")  # This will print the groups to the console
                # Redirect based on user's group
                try:
                    if user_is_student(user):
                        return redirect('student_success')
                    elif user_is_librarian(user):
                        return redirect('librarian_success')
                    elif user_is_schoolAdmin(user):
                        return redirect('book_page_views')
                    else:
                        messages.error(request, "You do not belong to any user group.")
                        return redirect('login_user')
                except Exception as e:
                    # Handle any unexpected errors
                    messages.error(request, "Error in redirection. Please try again.")
                    return redirect('login_user')
            else:
                # Return an 'invalid login' error message.
                messages.error(request, "Invalid username or password. Please try again.")
                return redirect('login_user')
        else:
            # If username or password is empty, return an error message.
            messages.error(request, "Please provide both username and password.")
            return redirect('login_user')
    else:
        return render(request, 'authenticate/login.html', {})

