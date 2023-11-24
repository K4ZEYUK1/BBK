from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Request, RequestStatus
from .forms import CreateRequestForm, ManageRequestForm, CreateUserForm, ManageUserForm
from django.shortcuts import redirect
from users.models import CustomUser, StandardHoliday
import copy
from datetime import timedelta, date, datetime
import calendar
import holidays
import pprint
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your views here.


def calculate_remaining_vacation_days(user, year=None):
    if not year:
        year = date.today().year

    used_vacation_days = calculate_vacation_usage(user=user, year=year)
    remaining_vacation_days = user.vacation_entitlement

    return remaining_vacation_days - used_vacation_days + user.manual_vacation_correction


def calculate_vacation_usage(user, year=None):
    if not year:
        year = date.today().year

    start_of_year = date(year, 1, 1)
    end_of_year = date(year, 12, 31)

    user_request_current_year = Request.objects.filter(requested_by=user, request_status=RequestStatus.ACCEPTED,
                                                       start_date__lte=end_of_year, end_date__gte=start_of_year)

    vacation_taken = 0

    for request in user_request_current_year:
        start_date = max(request.start_date, start_of_year)
        end_date = min(request.end_date, end_of_year)

        current_date = start_date

        while current_date <= end_date:
            if not StandardHoliday.objects.filter(date=current_date, province=user.province, country=user.country).exists():
                if current_date.weekday() in [0, 1, 2, 3, 4]:
                    vacation_taken += 1

            current_date += timedelta(days=1)

    return vacation_taken


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
        user: CustomUser = self.request.user

        context['requests'] = Request.objects.filter(requested_by=user)
        context['vacation_entitlement'] = user.vacation_entitlement
        context['vacation_taken'] = calculate_vacation_usage(user=user)
        context['remaining_vacation'] = calculate_remaining_vacation_days(user=user)

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

        if old_user_object.is_staff:
            new_user.is_staff = True

        if old_user_object.is_active:
            new_user.is_active = True

        if old_user_object.is_superuser:
            new_user.is_superuser = True

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

    def post(self, request, *args, **kwargs):

        year_selection = request.POST.get('year_selection')

        if year_selection == "next_year":
            current_year = self.request.session.get('selected_year')

            current_year += 1

            self.request.session['selected_year'] = current_year

        if year_selection == "previous_year":
            current_year = self.request.session.get('selected_year')

            current_year -= 1

            self.request.session['selected_year'] = current_year

        return redirect('.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.session.get('selected_year'):
            context["selected_year"] = datetime.now().year
            self.request.session['selected_year'] = context["selected_year"]
        else:
            context["selected_year"] = self.request.session.get('selected_year')

        year_dict = {"year": context["selected_year"], "months": []}

        month_dict = {
            "month_name": None,
            "month_number": None,
            "weeks": [],
        }

        day_dict = {
            "day_name": None,
            "day_number": None,
            "day_date": None,
            "entries": None,
            "holiday": None,
        }

        day_names = ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']

        first_day_of_year = date(year_dict["year"], 1, 1)
        last_day_of_year = date(year_dict["year"], 12, 31)

        all_requests_year = Request.objects.filter(start_date__lte=last_day_of_year, end_date__gte=first_day_of_year, request_status=RequestStatus.ACCEPTED)

        request_range = [
            (request.start_date, request.end_date) for request in all_requests_year
        ]

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
                
                current_week_dict[current_date_day]["entries"] = all_requests_year.filter(start_date__lte=current_day, end_date__gte=current_day)
                current_week_dict[current_date_day]["holiday"] = StandardHoliday.objects.filter(date=current_day, province=self.request.user.province, country=self.request.user.country)

                if current_day.weekday() == 6 or current_day == last_day:
                    current_month_dict["weeks"].append(current_week_dict)
                    current_week_dict = None

                current_day += timedelta(days=1)
            year_dict["months"].append(current_month_dict)

        context["selected_year_dict"] = year_dict

        return context





