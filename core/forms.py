from django import forms
from core.models import Friend,Group, Transactions
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
    class Meta():
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        help_texts = {
            'username': None
        }


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class NewGroup(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(NewGroup, self).__init__(*args, **kwargs)
        self.fields['userList'].queryset = Friend.objects.filter(user = user).values('friends').distinct()
    groupName = forms.CharField()
    userList = forms.ModelMultipleChoiceField(queryset=User.objects.all(),widget=forms.CheckboxSelectMultiple)

class AddFriendForm(forms.Form):
    email = forms.EmailField()

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = ('groupID', 'description', 'amount', 'paid_by', 'owed_by')