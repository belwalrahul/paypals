from django import forms
from core.models import Friend,Group
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

'''
class NewGroup(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(NewGroup, self).__init__(*args, **kwargs)
        self.fields['userList'].queryset = Friend.objects.filter(user = user).values('friends').distinct()
        name = forms.CharField()
    class Meta():
        model = Group
        fields = ('groupName', 'userList')
'''

class NewGroup(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(NewGroup, self).__init__(*args, **kwargs)
        self.fields['userList'].queryset = Friend.objects.filter(user = user).values('friends').distinct()
    groupName = forms.CharField()
    userList = forms.ModelMultipleChoiceField(queryset=User.objects.all(),widget=forms.CheckboxSelectMultiple)
