from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import Admin, User,Staff


class StaffSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username','email','phone_number',]
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_Staff = True
        user.save()
        Staffs = Staff.objects.create(user=user)
        return user

class AdminSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'phone_number']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_seller = True
        user.is_staff = True
        user.is_active = True
        if commit:
            user.save()
        Admins = Admin.objects.create(user=user)
        return user