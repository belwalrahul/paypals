from django.shortcuts import render, redirect
from core.forms import LoginForm, RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

# Create your views here.

@login_required(login_url='/login/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/login/')
def groups(request):
    return render(request, 'groups.html')

@login_required(login_url='/login/')
def add_transaction(request):
    return render(request, 'add_transaction.html')

@login_required(login_url='/login/')
def about(request):
    return render(request, 'about.html')


def callRegisterUserForm(request):
    if (request.method=='POST'):
        registerUserform = RegistrationForm(request.POST)
        if (registerUserform.is_valid()):
            # Save form data to DB
            user = registerUserform.save()
            # Encrypt the password
            user.set_password(user.password)
            # Save encrypted password to DB
            user.save()
            # Success! Redirect to home page.
            return redirect("/")
        else:
            # Form invalid, print errors to console
            return render(request, 'register.html', { "registerUserform": registerUserform , 'title':'User Registration'})
    
    else:
        if request.user.is_authenticated:
            return redirect("/")
        else:
            registerUserform = RegistrationForm()
            return render(request, 'register.html', { "registerUserform": registerUserform , 'title':'User Registration'})


def callUserLoginFn(request):
    
    if (request.method == 'POST'):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # First get the username and password supplied
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            # Django's built-in authentication function:
            user = authenticate(username=username, password=password)
            
            # If we have a user
            if user and user.is_superuser == False:
                #Check it the account is active
                if user.is_active:
                    # Log the user in.
                    login(request,user)
                    # Send the user back to homepage
                    return redirect("/")
                else:
                    # If account is not active:
                    return HttpResponse("Your account is not active.")
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(username,password))
                return render(request, 'login.html', {'login_form': LoginForm, 'title':'User Login', 'title':'Login'})
    else:
        # Nothing has been provided for username or password.
        return render(request, 'login.html', {'login_form': LoginForm, 'title':'User Login', 'title':'Login'})

@login_required(login_url='/login/')
def callUserLogOutFn(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return redirect("/")