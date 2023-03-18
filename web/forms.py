from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from web.models import ClientList


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'placeholder': 'Login'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class ConSettings(forms.Form):
    Hostname = forms.CharField(label='Hostname', required=False,
                               widget=forms.TextInput(attrs={'placeholder': ''}))
    Login = forms.CharField(label='Login', required=False, widget=forms.TextInput(attrs={'placeholder': ''}))
    Password = forms.CharField(label='Password', required=False,
                               widget=forms.TextInput(attrs={'placeholder': ''}))
    Endpoint = forms.CharField(label='Endpoint', required=False,
                               widget=forms.TextInput(attrs={'placeholder': ''}))
    MTU = forms.CharField(label='MTU', required=False, widget=forms.TextInput(attrs={'placeholder': ''}))
    Allowed_addr = forms.CharField(label='Allowed_addr', required=False,
                                   widget=forms.TextInput(attrs={'placeholder': ''}))
    DNS = forms.CharField(label='DNS', required=False, widget=forms.TextInput(attrs={'placeholder': ''}))
    Interface = forms.CharField(label='Interface', required=False,
                                widget=forms.TextInput(attrs={'placeholder': ''}))


class AddClient(forms.ModelForm):
    class Meta:
        model = ClientList
        fields = ['name']
