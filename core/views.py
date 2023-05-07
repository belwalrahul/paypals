from django.shortcuts import render, redirect
from core.forms import LoginForm, RegistrationForm, NewGroup, AddFriendForm, TransactionForm
from core.models import Friend, Transactions, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.models import User
# Create your views here.

@login_required(login_url='/login/')
def home(request):
    page_data = {}
    try:
        transactions = Transactions.objects.filter(paid_by = request.user)
        # print("----------------> " + transactions + " <----------------")a
        page_data = { "transactions": transactions }
    except Transactions.DoesNotExist:
        page_data = {}

    return render(request, 'home.html', page_data)

@login_required(login_url='/login/')
def groups(request):
    print(request.user.id)
    print(request.user.userList.all())
    groups = Group.objects.filter(userList = request.user.id)
    groupnames = [group.groupName for group in groups]
    members = [group.userList.all() for group in groups]
    for group in groups:
        print(group.groupName)
    page_data = { "groups": groups, "groupnames": groupnames, "members": members }
    return render(request, 'groups.html', page_data)

@login_required(login_url='/login/')
def add_groups(request):
    userList = Friend.objects.filter(user=request.user).values_list('friends__id', 'friends__username')
    userList = [User(id=friend[0], username=friend[1]) for friend in userList]
    if (request.method == "POST"):
        print("POST")
        Groupform = NewGroup(request.POST,userList=userList)
        if Groupform.is_valid():
            groupname = Groupform.cleaned_data['groupName']
            friends_list = Groupform.cleaned_data['userList'] | User.objects.filter(id=request.user.id)
            print(friends_list)
            group = Group.objects.create(groupName=groupname)
            group.userList.set(friends_list)
            group.save()
            return redirect('/groups')
        else:
            return redirect('/groups')
    else:
        Groupform = NewGroup(userList=userList)
        page_data = { "Groupform": Groupform  }
        return render(request, 'addgroups.html',page_data)

@login_required(login_url='/login/')
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            f_groupID = form.cleaned_data['groupID']
            f_description = form.cleaned_data['description']
            f_amount = form.cleaned_data['amount']
            f_paid_by = form.cleaned_data['paid_by']
            f_owed_by = form.cleaned_data['owed_by']

            transaction = Transactions.objects.create(groupID = f_groupID, description = f_description, amount = f_amount, paid_by = f_paid_by)
            transaction.owed_by.set(f_owed_by)
            transaction.save()

            return redirect('/')

    else:
        transaction_form = TransactionForm()
        page_data = { "transaction_form": transaction_form }

        return render(request, 'add_transaction.html', page_data)

@login_required(login_url='/login/')
def about(request):
    return render(request, 'about.html')

@login_required(login_url='/login/')
def friends_list(request):
    try:
        friend_obj = Friend.objects.get(user=request.user)
        # print(friend_obj.friends)
        friends = friend_obj.friends.all()
    except Friend.DoesNotExist:
        friends = []

    return render(request, 'friends_list.html', {'friends': friends})

@login_required(login_url='/login/')
def add_friend(request):
    if request.method == 'POST':
        form = AddFriendForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                friend = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'add_friend.html', {'form': form, 'error': 'User with this email does not exist.'})
            # friend_obj = Friend.objects.get(user=request.user)
            friend_obj = Friend.objects.get_or_create(user=request.user)
        # Add the friend to the current user's friends list
            if friend:
                friend_obj, created = Friend.objects.get_or_create(user=request.user)
                friend_obj.friends.add(friend)

            # Add the current user to the friend's friends list
                friend_obj, created = Friend.objects.get_or_create(user=friend)
                friend_obj.friends.add(request.user)

                return redirect('home.html')
            else:
                return render(request, 'add_friend.html', {'form': form})
    else:
        form = AddFriendForm()
    return render(request, 'add_friend.html', {'form': form})


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

@login_required(login_url='/login/')
def grouppage(request,id):
    group = Group.objects.get(groupID=id)
    page_data = { "group": group  }
    return render(request, 'grouppage.html',page_data)

@login_required(login_url='/login/')
def add_grouptransaction(request,id):
    group = Group.objects.get(groupID=id)
    page_data = { "group": group  }
    if request.method == 'POST':
        print("inside post")
    else:
        return render(request, 'addgrouptrans.html',page_data)
    