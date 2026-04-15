from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # Called when registering a normal user
        if not email:
            raise ValueError('An email address is required.')
        email = self.normalize_email(email)  
        user  = self.model(email=email, **extra_fields)  
        user.set_password(password) # hash the password
        user.save(using=self._db)            
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Called by: python manage.py createsuperuser
        extra_fields.setdefault('is_staff', True)  # allow Django admin access
        extra_fields.setdefault('is_superuser', True)  # all permissions granted
        extra_fields.setdefault('role', 'super_admin') # assign highest role
        return self.create_user(email, password, **extra_fields)

#  Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),  
        ('admin', 'Admin'),           
        ('regular_user', 'Regular User'), 
    ]

    # Fields stored in the database
    email = models.EmailField(unique=True)   
    role = models.CharField(
                    max_length=20,
                    choices=ROLE_CHOICES,
                    default='regular_user'     
                 )
    is_active = models.BooleanField(default=True)   # False = account disabled
    is_staff = models.BooleanField(default=False)  # True = can access Django admin panel

    objects = CustomUserManager()   

    USERNAME_FIELD  = 'email'       
    REQUIRED_FIELDS = []         

    def __str__(self):
        return self.email

    # Permission helper methods
    # Django templates can call these as: {% if request.user.can_create %}

    def can_create(self):
        return self.role in ['super_admin', 'admin']

    def can_update(self):
        return self.role in ['super_admin', 'admin']

    def can_delete(self):
        return self.role == 'super_admin'