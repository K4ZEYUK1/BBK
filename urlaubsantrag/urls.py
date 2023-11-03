from django.urls import path
from django.views.generic import TemplateView
from django.conf.urls.static import static

from . import views

from django.conf import settings

app_name = 'urlaubsantrag'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name="LandingPageView"),
    path('create/request/', views.CreateRequestView.as_view(), name="RequestPageView"),
    path('request_administration/', views.RequestAdministrationView.as_view(), name="RequestAdministrationView"),
    path('request_details/<int:pk>/', views.RequestDetailView.as_view(), name="RequestDetailView"),
    path('create/user/', views.CreateUserView.as_view(), name="CreateUserView"),
    path('manage/user/<int:pk>/', views.ManageUserView.as_view(), name="ManageUserView"),
    path('user_overview/', views.UserOverviewView.as_view(), name="UserOverviewView"),
    path('calender/', views.CalenderView.as_view(), name="CalenderView"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)