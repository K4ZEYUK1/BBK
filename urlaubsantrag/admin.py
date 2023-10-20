from django.contrib import admin
from .models import Request

# Register your models here.

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    class Meta:
        model = Request
        fields = '__all__'