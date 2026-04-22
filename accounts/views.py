from django.shortcuts import redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView
from kombu.exceptions import OperationalError

from .forms import RegisterForm, LoginForm, OTPVerificationForm
from .tasks import send_welcome_email, send_otp_email

User = get_user_model()


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('contact_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()

        try:
            send_welcome_email.delay(user.email, user.get_full_name() or user.email)
        except OperationalError:
            messages.warning(
                self.request,
                'Account created, but welcome email was not sent because Celery/Redis is not running.'
            )

        messages.success(self.request, 'Account created successfully. Please log in.')
        return super().form_valid(form)


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('verify_otp')

    def form_valid(self, form):
        user = form.get_user()

        if not user.is_active:
            form.add_error(None, 'Your account has been disabled.')
            return self.form_invalid(form)

        otp = user.generate_otp()

        try:
            send_otp_email.delay(user.email, otp, user.get_full_name() or user.email)
        except OperationalError:
            form.add_error(None, 'OTP email could not be sent because Celery/Redis is not running.')
            return self.form_invalid(form)

        self.request.session['pending_user_id'] = user.pk
        messages.info(self.request, f'OTP sent to {user.email}. Check your inbox.')
        return redirect('verify_otp')


class OTPVerificationView(FormView):
    template_name = 'accounts/otp_verify.html'
    form_class = OTPVerificationForm
    success_url = reverse_lazy('contact_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('pending_user_id'):
            messages.warning(request, 'Please log in first.')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        pending_user_id = self.request.session.get('pending_user_id')
        otp_input = form.cleaned_data['otp_code']

        try:
            user = User.objects.get(pk=pending_user_id)
        except User.DoesNotExist:
            messages.error(self.request, 'User not found. Please log in again.')
            return redirect('login')

        if not user.is_otp_valid(otp_input):
            form.add_error('otp_code', 'Invalid OTP. Please try again.')
            return self.form_invalid(form)

        user.clear_otp()
        self.request.session.pop('pending_user_id', None)
        login(self.request, user)
        messages.success(self.request, f'Welcome back, {user.get_full_name() or user.email}!')
        return super().form_valid(form)


class LogoutView(BaseLogoutView):
    next_page = reverse_lazy('login')