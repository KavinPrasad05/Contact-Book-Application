# accounts/urls.py

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    OTPVerificationView,
    LogoutView,
)

urlpatterns = [
    path('register/',   RegisterView.as_view(),        name='register'),
    path('login/',      LoginView.as_view(),            name='login'),
    path('verify-otp/', OTPVerificationView.as_view(),  name='verify_otp'),
    path('logout/',     LogoutView.as_view(),           name='logout'),
]