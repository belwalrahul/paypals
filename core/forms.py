from django import forms
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.CharField(widget=forms.TextInput)
    first_name = forms.CharField(widget=forms.TextInput)
    last_name = forms.CharField(widget=forms.TextInput)

class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
