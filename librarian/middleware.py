# userauth/middleware.py

from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
import time
from django.shortcuts import redirect

class InactivityLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        current_time = time.time()
        last_activity = request.session.get('last_activity', current_time)

        # Calculate the time difference
        elapsed_time = current_time - last_activity

        # If the elapsed time exceeds the session timeout, log out the user
        if elapsed_time > settings.SESSION_COOKIE_AGE:
            logout(request)
            return

        # Update the last activity time in the session
        request.session['last_activity'] = current_time


class UserRedirect(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            if request.path == '/':
                return redirect('librarian')
        else:
            if request.path == '/':
                return redirect('userauth:login_user')