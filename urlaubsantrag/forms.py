from django import forms
from django.forms import DateInput
from .models import Request, RequestStatus
from django.contrib.auth.models import User
from users.models import CustomUser


class DateInputWidget(DateInput):
    input_type = 'date'


class CreateRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['start_date', 'end_date']
        labels = {
            'start_date': 'Anfangsdatum',
            'end_date': 'Enddatum'
        }


class CreateUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password', 'abbreviation', 'staff_nr', 'department', 'employee_admin_level', 'country']
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail-Adresse',
            'password': 'Passwort',
            'abbreviation': 'Kürzel',
            'staff_nr': 'Mitarbeiternummer',
            'employee_admin_level': 'Berechtigungen',
            'country': 'Land',
            'department': 'Abteilung',
        }


class ManageUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password', 'abbreviation', 'staff_nr', 'is_active',
                  'employee_admin_level', 'department', 'country']
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail-Adresse',
            'password': 'Passwort',
            'abbreviation': 'Kürzel',
            'staff_nr': 'Mitarbeiternummer',
            'is_active': 'Aktiv',
            'employee_admin_level': 'Berechtigungen',
            'department': 'Abteilung',
            'country': 'Land'
        }


class ManageRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['declinement_reason']
        labels = {
            'declinement_reason': 'Ablehnungsgrund',
        }