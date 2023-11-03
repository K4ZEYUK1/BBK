from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Request, RequestStatus
from django.contrib.auth.models import User
from .forms import CreateRequestForm, ManageRequestForm, CreateUserForm, ManageUserForm
from django.shortcuts import redirect
from users.models import CustomUser



# Create your views here.

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





