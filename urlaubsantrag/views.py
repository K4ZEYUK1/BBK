from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Request, RequestStatus
from django.contrib.auth.models import User
from .forms import CreateRequestForm, ManageRequestForm, CreateUserForm, ManageUserForm
from django.shortcuts import redirect
from users.models import CustomUser
import copy
from datetime import timedelta, date, datetime
import calendar
import holidays
import pprint


# Create your views here.

month_names_german = {
            'January': 'Januar',
            'February': 'Februar',
            'March': 'März',
            'April': 'April',
            'May': 'Mai',
            'June': 'Juni',
            'July': 'Juli',
            'August': 'August',
            'September': 'September',
            'October': 'Oktober',
            'November': 'November',
            'December': 'Dezember'
        }


class CheckPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect("/")


class LandingPageView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/login/'
    template_name = "urlaubsantrag/landingpage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['requests'] = Request.objects.filter(requested_by=user)

        return context


class CreateRequestView(LoginRequiredMixin, generic.CreateView):
    login_url = '/login/'
    template_name = "urlaubsantrag/create_request.html"
    model = Request
    form_class = CreateRequestForm

    def form_valid(self, form):
        new_request = form.save(commit=False)
        request_start_date = form.cleaned_data["start_date"]
        request_end_date = form.cleaned_data["end_date"]

        if request_start_date > request_end_date:
            form.add_error("start_date", "Das Startdatum darf nicht nach dem Enddatum sein!")
            return self.form_invalid(form)

        new_request.requested_by = self.request.user
        new_request.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class RequestAdministrationView(LoginRequiredMixin, CheckPermissionMixin, generic.TemplateView):
    login_url = '/login/'
    template_name = "urlaubsantrag/request_administration.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['requests'] = Request.objects.all().order_by("-start_date")

        return context


class RequestDetailView(LoginRequiredMixin, CheckPermissionMixin, generic.DetailView):
    login_url = '/login/'
    template_name = "urlaubsantrag/request_details.html"
    model = Request

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_button'] = True
        return context

    def post(self, request, *args, **kwargs):
        user_request = self.get_object()

        if 'withdraw' in request.POST:
            if user_request.request_status == RequestStatus.NEW:
                if user_request.requested_by == self.request.user:
                    user_request.delete()

            return redirect('/request_administration/')

        elif 'decline' in request.POST:
            if user_request.request_status == RequestStatus.NEW:
                if self.request.user.is_staff:
                    user_request.request_status = RequestStatus.DENIED
                    user_request.save()
            return redirect('/request_administration/')

        elif 'approve' in request.POST:
            if user_request.request_status == RequestStatus.NEW:
                if self.request.user.is_staff:
                    user_request.request_status = RequestStatus.ACCEPTED
                    user_request.save()
            return redirect('/request_administration/')

        else:
            return super().post(request, *args, **kwargs)


class RequestManagementView(LoginRequiredMixin, CheckPermissionMixin, generic.UpdateView):
    login_url = '/login/'
    template_name = "urlaubsantrag/request_management.html"
    model = Request
    form_class = ManageRequestForm


class CreateUserView(LoginRequiredMixin, generic.CreateView):
    login_url = '/login/'
    template_name = "urlaubsantrag/create_user.html"
    model = CustomUser
    form_class = CreateUserForm

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ManageUserView(LoginRequiredMixin, generic.UpdateView):
    login_url = '/login/'
    template_name = "urlaubsantrag/manage_user.html"
    model = CustomUser
    form_class = ManageUserForm

    def form_valid(self, form):
        new_user = form.save(commit=False)
        old_user_object = self.get_object()
        if form.cleaned_data['password'] == "stop":
            new_user.password = old_user_object.password
        else:
            new_user.set_password(form.cleaned_data['password'])
        new_user.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UserOverviewView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/login/'
    template_name = "urlaubsantrag/user_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['users'] = CustomUser.objects.all()

        return context

class CalenderView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/login/'
    template_name = "urlaubsantrag/calender.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year_dict = {"year": 2023, "months": []}

        month_dict = {
            "month_name": None,
            "month_number": None,
            "weeks": []
        }

        day_dict = {
            "day_name": None,
            "day_number": None,
            "day_date": None,
        }

        day_names = ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']

        for month in range(1, 13):
            current_month_dict = copy.deepcopy(month_dict)

            first_day = date(year_dict["year"], month, 1)
            last_day = date(year_dict["year"], month, calendar.monthrange(year_dict["year"], month)[1])

            current_month_dict["month_name"] = month_names_german.get(first_day.strftime('%B'), '')
            current_month_dict["month_number"] = month

            current_day = first_day

            week_dict = {}

            while current_day <= last_day:

                current_day_number = current_day.strftime('%d')
                current_date_day = day_names[current_day.weekday()]
                current_day_date = current_day.strftime('%Y-%m-%d')

                try:
                    current_week_dict[current_date_day] = copy.deepcopy(day_dict)
                except:
                    current_week_dict = copy.deepcopy(week_dict)
                    current_week_dict[current_date_day] = copy.deepcopy(day_dict)

                current_week_dict[current_date_day]["day_name"] = current_date_day
                current_week_dict[current_date_day]["day_number"] = current_day_number
                current_week_dict[current_date_day]["day_date"] = current_day_date

                if current_day.weekday() == 6:
                    current_month_dict["weeks"].append(current_week_dict)
                    current_week_dict = None

                current_day += timedelta(days=1)
            year_dict["months"].append(current_month_dict)

        context["selected_year_dict"] = year_dict

        return context





