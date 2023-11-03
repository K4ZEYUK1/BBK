from django.db import models
import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, User, AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, ValidationError, MaxValueValidator, MinValueValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email ist Pflicht!')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30, blank=False)
    required_employees = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(500)])

    def __str__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return f"/"


class EmployeeAdministrationLevel(models.TextChoices):
    EMPLOYEE = 'EMP', _('Mitarbeiter')
    SUPERVISOR = 'SUP', _('Teamleiter')
    HEAD_OF_DEPARTMENT = 'HOD', _('Abteilungsleiter')
    ADMIN = 'ADM', _('Administration')


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    employee_admin_level = models.CharField(max_length=3, choices=EmployeeAdministrationLevel.choices, default=EmployeeAdministrationLevel.EMPLOYEE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)

    abbreviation = models.CharField(max_length=3)
    staff_nr = models.CharField(max_length=6)
    country = CountryField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_absolute_url(self):
        return f"/"
