from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

#  Registration Form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )
    class Meta:
        model = CustomUser
        fields = ['email']
        

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class':       'form-control',
            'placeholder': 'Enter your email',
            'autofocus':   True,
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Enter your password',
        })
    )
class OTPVerificationForm(forms.Form):
    """Step 2 of 2FA — collect the 6-digit OTP sent to the user's email."""
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class':        'form-control text-center',
            'placeholder':  'Enter 6-digit OTP',
            'autofocus':    True,
            'inputmode':    'numeric',
            'pattern':      '[0-9]{6}',
            'autocomplete': 'one-time-code',
        }),
        label='OTP Code',
    )

    def clean_otp_code(self):
        otp = self.cleaned_data.get('otp_code', '').strip()
        if not otp.isdigit():
            raise forms.ValidationError('OTP must contain digits only.')
        if len(otp) != 6:
            raise forms.ValidationError('OTP must be exactly 6 digits.')
        return otp