from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', 'regular_user')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('regular_user', 'Regular User'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='regular_user')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_otp_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name or self.email

    def get_group_name(self):
        group = self.groups.first()
        return group.name if group else 'No Group'

    def generate_otp(self):
        import random
        otp = str(random.randint(100000, 999999))
        self.otp_code = otp
        self.otp_created_at = timezone.now()
        self.is_otp_verified = False
        self.save(update_fields=['otp_code', 'otp_created_at', 'is_otp_verified'])
        return otp

    def is_otp_valid(self, otp_input):
        return self.otp_code == otp_input

    def clear_otp(self):
        self.otp_code = None
        self.otp_created_at = None
        self.is_otp_verified = True
        self.save(update_fields=['otp_code', 'otp_created_at', 'is_otp_verified'])

    @property
    def is_admin(self):
        return self.role in ['admin', 'super_admin'] or self.is_staff or self.is_superuser

    def can_create(self):
        return self.role in ['admin', 'super_admin'] or self.is_superuser

    def can_update(self):
        return self.role in ['admin', 'super_admin'] or self.is_superuser

    def can_delete(self):
        return self.role == 'super_admin' or self.is_superuser