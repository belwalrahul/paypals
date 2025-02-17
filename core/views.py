from django.shortcuts import render, redirect
from core.forms import LoginForm, RegistrationForm, NewGroup, AddFriendForm, TransactionForm, GroupTransactionForm
from core.models import Friend, Transactions, Group, FriendRequests
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
import requests
from django.conf import settings


# Create your views here.

import csv
from django.http import HttpResponse

@login_required(login_url='/login/')
def download_transactions(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['DESCRIPTION', 'PAID_BY', 'OWED_BY', 'AMOUNT_OWED'])

    transactions = Transactions.objects.filter(paid_by=request.user) | Transactions.objects.filter(owed_by=request.user)

    for transaction in transactions:
        owed_by_list = ""
        for member in transaction.owed_by.all():
            owed_by_list += member.username + ", "
        writer.writerow([transaction.description, transaction.paid_by, owed_by_list, transaction.amount])

    return response



@login_required(login_url='/login/')
def home(request):
    page_data = {}
    transaction_data = {}
    # group = { 0: "Individual Group" }
    total_paid = 0
    total_owed = 0
    try:
        transactions = Transactions.objects.filter(owed_by = request.user)
        transactions_paid = Transactions.objects.filter(paid_by = request.user)

        for paid in transactions_paid:
            noOfPeople = paid.owed_by.count()
            total_paid += ((paid.amount / noOfPeople) * (noOfPeople-1))
        for owed in transactions:
            if owed.paid_by != request.user:
                noOfPeople = owed.owed_by.count()
                if owed.paid_by != request.user:
                    total_owed += (owed.amount / noOfPeople)
                else:
                    total_owed -= (owed.amount / noOfPeople)

        group = "Individual Group"
        
        for transaction in transactions:
            # print(transaction)
            group = "Individual Group"

            if transaction.groupID != 0:
                group_name = Group.objects.get(groupID = transaction.groupID)
                # group[transaction.groupID] = group_name.groupName
                group = group_name.groupName

            # print(group)
            transaction_data[transaction] = [ transaction.owed_by.all(), group ]
        # print("----------------> " + transactions + " <----------------")a
        page_data = { "transactions": transaction_data, "owed": total_paid, "owe": total_owed, "group": group }
    except Transactions.DoesNotExist:
        page_data = {}

    # print(page_data)

    return render(request, 'paypals/home.html', page_data)

@login_required(login_url='/login/')
def groups(request):
    groups = Group.objects.filter(userList = request.user.id)
    groupnames = [group.groupName for group in groups]
    members = [group.userList.all() for group in groups]
    page_data = { "groups": groups, "groupnames": groupnames, "members": members }
    return render(request, 'paypals/groups.html', page_data)

@login_required(login_url='/login/')
def account_settings(request):

    return render(request, 'paypals/account_settings.html')


@login_required(login_url='/login/')
def add_groups(request):
    userList = Friend.objects.filter(user=request.user).values_list('friends__id', 'friends__username')
    userList = [User(id=friend[0], username=friend[1]) for friend in userList]
    if (request.method == "POST"):
        Groupform = NewGroup(request.POST,userList=userList)
        if Groupform.is_valid():
            groupname = Groupform.cleaned_data['groupName']
            friends_list = Groupform.cleaned_data['userList'] | User.objects.filter(id=request.user.id)
            group = Group.objects.create(groupName=groupname)
            group.userList.set(friends_list)
            group.save()
            return redirect('/groups')
        else:
            return redirect('/groups')
    else:
        Groupform = NewGroup(userList=userList)
        page_data = { "Groupform": Groupform  }
        return render(request, 'paypals/addgroups.html',page_data)


@login_required(login_url='/login/')
def delete_transaction(request, pk):
    group_id = 0
    try:
        transaction = Transactions.objects.get(id=pk)
        if transaction.paid_by == request.user:
            if transaction.groupID != 0:
                group_id = transaction.groupID
            transaction.delete()
            messages.success(request, 'Transaction deleted successfully.')
        else:
            # TODO @jait send data to modal/ toast on frontend
            messages.error(request, 'You are not authorized to delete this transaction.')
    except Transactions.DoesNotExist:
        # lets just keep this on the backend
        messages.error(request, 'Transaction does not exist.')
    return redirect('/')

@login_required(login_url='/login/')
def delete_group(request, pk):
    try:
        group = Group.objects.get(groupID = pk)
        group.delete()
        messages.success(request, 'Group deleted successfully.')

        transactions = Transactions.objects.filter(groupID=pk)
        for transaction in transactions:
            transaction.delete()
        
    except Transactions.DoesNotExist:
        # lets just keep this on the backend
        messages.error(request, 'Transaction does not exist.')
    return redirect('/groups/')

@login_required(login_url='/login/')
def add_transaction(request):
    friends = Friend.objects.get(user=request.user).friends.all() # get the user's friends
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            f_description = form.cleaned_data['description']
            f_amount = form.cleaned_data['amount']
            f_paid_by = form.cleaned_data['paid_by'] 
            f_owed_by = form.cleaned_data['owed_by'] | User.objects.filter(id=request.user.id)
            
            transaction = Transactions.objects.create(groupID = 0, description = f_description, amount = f_amount, paid_by = f_paid_by)
            transaction.owed_by.set(f_owed_by)
            transaction.save()

            return redirect('/')
    else:
        transaction_form = TransactionForm()
        paid_by_list = friends | User.objects.filter(id=request.user.id)
        transaction_form.fields['owed_by'].queryset = paid_by_list.distinct() # limit the queryset to the user's friends
        transaction_form.fields['paid_by'].queryset = paid_by_list.distinct() # limit the queryset to the user's friends
        page_data = { "transaction_form": transaction_form }

        return render(request, 'paypals/add_transaction.html', page_data)

@login_required(login_url='/login/')
def about(request):
    return render(request, 'paypals/about.html')

@login_required(login_url='/login/')
def remove_friend(request, friend_id):
    try:
        friend = User.objects.get(id=friend_id)
        friend_obj = Friend.objects.get(user=request.user)
        if friend in friend_obj.friends.all():
            friend_obj.friends.remove(friend)
            friend_obj, created = Friend.objects.get_or_create(user=friend)
            friend_obj.friends.remove(request.user)
            messages.success(request, f'{friend.username} has been removed from your friends list.')
        else:
            messages.error(request, f'{friend.username} is not in your friends list.')
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
    except Friend.DoesNotExist:
        messages.error(request, 'You do not have any friends yet.')
    return redirect('/friends/')

@login_required(login_url='/login/')
def friends_list(request):
    try:
        friend_obj = Friend.objects.get(user=request.user)
        friends = friend_obj.friends.all()
    except Friend.DoesNotExist:
        friends = []
    return render(request, 'paypals/friends_list.html', {'friends': friends})

@login_required(login_url='/login/')
def add_friend(request):
    if request.method == 'POST':
        form = AddFriendForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                friend = User.objects.get(email=email)
                friends_list = Friend.objects.get(user=request.user)
                if friend in friends_list.friends.all():
                    messages.error(request, f'{friend.username} is already in your friends list.')
                else:
                    if not(FriendRequests.objects.filter(from_user=request.user, to_user=friend).exists() or FriendRequests.objects.filter(from_user=friend, to_user=request.user).exists()):
                        FriendRequests.objects.create(from_user=request.user, to_user=friend).save()
                    else:
                        messages.error(request, 'Friend request already sent.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email.')
                return render(request, 'paypals/add_friend.html', {'form': form, 'error': 'User with this email does not exist.'})
            return redirect('/friends/')
        else:
            return render(request, 'paypals/add_friend.html', {'form': form})
    else:
        form = AddFriendForm()
    return render(request, 'paypals/add_friend.html', {'form': form})


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
            return render(request, 'paypals/register.html', { "registerUserform": registerUserform , 'title':'User Registration'})
    
    else:
        if request.user.is_authenticated:
            return redirect("/")
        else:
            registerUserform = RegistrationForm()
            return render(request, 'paypals/register.html', { "registerUserform": registerUserform , 'title':'User Registration'})


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
                return render(request, 'paypals/login.html', {'login_form': LoginForm, 'title':'User Login', 'title':'Login'})
    else:
        # Nothing has been provided for username or password.
        return render(request, 'paypals/login.html', {'login_form': LoginForm, 'title':'User Login', 'title':'Login'})

@login_required(login_url='/login/')
def callUserLogOutFn(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return redirect("/")

@login_required(login_url='/login/')
def grouppage(request,id):
    group = Group.objects.get(groupID=id)
    userList = group.userList.all()
    values = {}
   
    for user in userList:
        if user != request.user:
            values[user.username] = 0 
    
    page_data = {}
    transaction_data = {}
    try:
        transactions = Transactions.objects.filter(groupID = id)
        
        for transaction in transactions:
            transaction_data[transaction] = transaction.owed_by.all()
            amount_per_person = transaction.amount / transaction.owed_by.count()
            if transaction.paid_by == request.user:
                for user in transaction.owed_by.values():
                    if user['username'] != str(request.user):
                        values[user['username']] -= amount_per_person
            else:
                for user in transaction.owed_by.values():
                    if user['username'] == str(request.user):
                        values[str(transaction.paid_by)] += amount_per_person

        owed = {}
        borrowed = {}
        neutral = {}
        for user in userList:
            if(user.username != str(request.user)):
                if values[user.username] > 0:
                    owed[user.username] = values[user.username]
                elif values[user.username] < 0:
                    borrow = abs(values[user.username])
                    borrowed[user.username] = borrow
                else:
                    neutral[user.username] = values[user.username]

        page_data = {"group": group, "transactions": transaction_data,"owed":owed,"borrowed":borrowed,"neutral":neutral}
    except Transactions.DoesNotExist:
        page_data = {"group": group}
    return render(request, 'paypals/grouppage.html',page_data)

@login_required(login_url='/login/')
def add_grouptransaction(request,id):
    group = Group.objects.get(groupID=id)
    userList = group.userList.all()
    page_data = { "group": group  }
    if request.method == 'POST':
        form = GroupTransactionForm(request.POST,owed_by=userList)
        if form.is_valid():
            f_description = form.cleaned_data['description']
            f_amount = form.cleaned_data['amount']
            f_paid_by = form.cleaned_data['paid_by']
            f_owed_by = form.cleaned_data['owed_by'] | User.objects.filter(id=request.user.id)
            
            transaction = Transactions.objects.create(groupID = id, description = f_description, amount = f_amount, paid_by = f_paid_by)
            transaction.owed_by.set(f_owed_by)
            
            transaction.save()
            rdr = "/groups/"+str(id)+"/add"
            return redirect(grouppage,id=id)
    else:
        transaction_form = GroupTransactionForm(owed_by=userList)
        page_data = { "transaction_form": transaction_form }
        return render(request, 'paypals/addgrouptrans.html',page_data)
@login_required(login_url='/login/')
def friend_request(request):
    if request.method == 'POST':
        requests = []
        return render(request, 'paypals/friend_request.html',{"requests":requests})
    else:
        try:
            requests = FriendRequests.objects.filter(to_user=request.user).all()
        except FriendRequests.DoesNotExist:
            requests = []
        return render(request, 'paypals/friend_request.html',{"requests":requests})

def remove_request(request,id):
    req = FriendRequests.objects.get(id=id)
    req.delete()
    messages.success(request,'Request removed.')
    return redirect('/friend_request/')

def accept_request(request,id):
    newfriend = User.objects.get(id=id)
    if newfriend:
        friend_obj,created = Friend.objects.get_or_create(user=request.user)
        friend_obj.friends.add(newfriend)
        friend_obj,created = Friend.objects.get_or_create(user=newfriend)
        friend_obj.friends.add(request.user)
        messages.success(request,'Friend added.')
    else:
        messages.error(request,'Error adding friend.')
    req = FriendRequests.objects.get(from_user=newfriend,to_user=request.user)
    req.delete()
    return redirect('/friend_request/')
    

def server_info(request):
    server_geodata = requests.get('https://ipwhois.app/json/').json()
    settings_dump = settings.__dict__
    return HttpResponse("{}{}".format(server_geodata, settings_dump))