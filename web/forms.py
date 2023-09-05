from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import ClientList, Settings


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'autocomplete': 'someRandomString'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'autocomplete': 'someRandomString'}))


# class ConSettings(forms.Form):
#     Host = forms.CharField(label='Host', required=False,
#                                widget=forms.TextInput(attrs={'placeholder': ''}))
#     Login = forms.CharField(label='Login', required=False, widget=forms.TextInput(attrs={'placeholder': ''}))
#     Password = forms.CharField(label='Password', required=False,
#                                widget=forms.TextInput(attrs={'placeholder': ''}))
#     Endpoint = forms.CharField(label='Endpoint', required=False,
#                                widget=forms.TextInput(attrs={'placeholder': ''}))
#     MTU = forms.CharField(label='MTU', required=False, widget=forms.TextInput(attrs={'placeholder': ''}))
#     Network = forms.CharField(label='Network', required=False,
#                                    widget=forms.TextInput(attrs={'placeholder': ''}))
#     DNS = forms.CharField(label='DNS', required=False, widget=forms.TextInput(attrs={'placeholder': ''}))
#     Interface = forms.CharField(label='Interface', required=False,
#                                 widget=forms.TextInput(attrs={'placeholder': ''}))


class AddClient(forms.ModelForm):
    class Meta:
        model = ClientList
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'name_field', 'id': 'Name',
                                           'pattern': '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{1,63}$'})
        }

class ConSettings(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['Host', 'Username', 'Password',
        'Endpoint', 'Network', 'Interface', 'MTU', 'DNS']