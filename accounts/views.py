from django.contrib.auth.views import LogoutView as BaseLogoutView, LoginView as BaseLoginView
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import RegisterForm, LoginForm
from .models import CustomUser

class RegisterView(FormView):
    form_class    = RegisterForm
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('contact_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return str(reverse_lazy('login')) + '?registered=true'

class LoginView(BaseLoginView):
    form_class    = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    def form_invalid(self, form):
        email = self.request.POST.get('username', '')
        if not CustomUser.objects.filter(email__iexact=email).exists():
            form.errors.clear()
            form.add_error('username', 'This email is not registered.')
        else:
            form.add_error('password', 'Incorrect password')

        return self.render_to_response(self.get_context_data(form=form))

class LogoutView(BaseLogoutView):
    pass