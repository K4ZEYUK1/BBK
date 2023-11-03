from django.contrib import admin
from django import forms
from .models import Department, CustomUser


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    class Meta:
        model = Department
        fields = '__all__'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    class Meta:
        model = CustomUser
        fields = '__all__'
