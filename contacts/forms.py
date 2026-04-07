from django import forms
from .models import Contact
import re


class ContactForm(forms.ModelForm):
    class Meta:
        model  = Contact
        fields = ['name', 'phone_number', 'email', 'contact_picture', 'contact_group']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email (optional)'
            }),
            'contact_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'contact_group': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Name must be at least 2 characters.')
        return name

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        pattern = r'^\+?[\d\s\-\(\)]{7,15}$'
        if not re.match(pattern, phone):
            raise forms.ValidationError(
                'Enter a valid phone number'
            )
        qs = Contact.objects.filter(phone_number=phone)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                'A contact with this phone number already exists.'
            )
        return phone
