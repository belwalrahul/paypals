from django.shortcuts import render
from core.forms import LoginForm, RegistrationForm

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login(request):
    #TODO add condition to handle post request from login form
    return render(request, 'login.html', {'login_form':LoginForm})

def register(request):
    return render(request, 'register.html', {'register_form': RegistrationForm})