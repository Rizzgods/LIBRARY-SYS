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
            response = redirect('userauth:login_user')
            response['X-Logged-Out'] = 'true'  # Custom header to indicate logout
            return response

        # Update the last activity time in the session
        request.session['last_activity'] = current_time

    def process_response(self, request, response):
        if request.user.is_authenticated:
            # Restart the session cookie age
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

        return response




from django.urls import NoReverseMatch, reverse
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

class HandleNoReverseMatchMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, NoReverseMatch):
            logger.error(f"NoReverseMatch: {exception} on URL: {request.path}")
            if 'user-login' in str(exception):
                return redirect('login_user')
            
        return None