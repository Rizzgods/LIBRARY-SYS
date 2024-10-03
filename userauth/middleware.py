# userauth/middleware.py

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse
from django.utils.deprecation import MiddlewareMixin
import time

class HandleNoReverseMatchMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, NoReverseMatch):
            return redirect('userauth:login_user')
        return None

class SessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Prevent infinite redirection loop
        if request.path == reverse('userauth:login_user'):
            return None

        current_time = time.time()
        last_activity = request.session.get('last_activity', current_time)

        elapsed_time = current_time - last_activity

        # Debugging information
        print(f"Current time: {current_time}")
        print(f"Last activity: {last_activity}")
        print(f"Elapsed time: {elapsed_time}")
        print(f"Session cookie age: {settings.SESSION_COOKIE_AGE}")

        if elapsed_time > settings.SESSION_COOKIE_AGE:
            logout(request)
            response = redirect('userauth:login_user')
            response['X-Logged-Out'] = 'true'  # Custom header to indicate logout
            return response

        # Update the last activity time in the session
        request.session['last_activity'] = current_time