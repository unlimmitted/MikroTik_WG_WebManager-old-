from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import ClientList, Settings


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(error_messages={'required': 'Please enter your name'},
                               label='Логин', widget=forms.TextInput(
            attrs={'autocomplete': 'someRandomString'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(
        attrs={'autocomplete': 'someRandomString'}))


class AddClient(forms.ModelForm):
    class Meta:
        model = ClientList
        fields = ['Name']
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'name_field', 'id': 'Name',
                                           'pattern': '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{1,63}$'})
        }

class MTSettings(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['host', 'username', 'password',
                  'server_listen_port', 'server_endpoint',
                  'client_private_key',
                  'client_public_key', 'client_endpoint',
                  'client_endpoint_port', 'client_preshared_key',
                  'client_address', 'local_network']
        widgets = {
            'host': forms.TextInput(attrs={'placeholder': '0.0.0.0'}),
            'username': forms.TextInput(attrs={'placeholder': 'admin'}),
            'password': forms.TextInput(attrs={'type': 'password'}),
            'server_listen_port': forms.TextInput(attrs={'placeholder': '12038'}),
            'server_endpoint': forms.TextInput(attrs={'placeholder': '0.0.0.0'}),
            'client_private_key': forms.TextInput(attrs={'type': 'password'}),
            'client_endpoint': forms.TextInput(attrs={'placeholder': '0.0.0.0'}),
            'client_endpoint_port': forms.TextInput(attrs={'placeholder': '51820'}),
            'client_address': forms.TextInput(attrs={'placeholder': '0.0.0.0/0'}),
            'local_network': forms.TextInput(attrs={'placeholder': '0.0.0.0/0'}),
            'client_preshared_key': forms.TextInput(attrs={'type': 'password'})
        }
