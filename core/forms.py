from django import forms
from django.db.models import Q
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


class NewGroup(forms.ModelForm):
    userList = forms.ModelMultipleChoiceField(queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,)
    class Meta:
        model = Group
        fields = ['groupName', 'userList']
    def __init__(self, *args, **kwargs):
        friends_list = kwargs.pop('userList')
        super().__init__(*args, **kwargs)
        self.fields['userList'].queryset = User.objects.filter(
            Q(id__in=[friend.id for friend in friends_list])
        )

class AddFriendForm(forms.Form):
    email = forms.EmailField()

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transactions
        fields = ('description', 'amount', 'paid_by', 'owed_by')

class GroupTransactionForm(forms.ModelForm):
    owed_by = forms.ModelMultipleChoiceField(queryset=User.objects.none(), widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Transactions
        fields = ('description', 'amount', 'paid_by', 'owed_by')

