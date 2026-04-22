from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta


class IdleTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity')

            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if timezone.is_naive(last_activity):
                    last_activity = timezone.make_aware(last_activity, timezone.get_current_timezone())

                if current_time - last_activity > timedelta(minutes=10):
                    logout(request)
                    request.session.flush()
                    return redirect('login')

            request.session['last_activity'] = current_time.isoformat()

        response = self.get_response(request)
        return response