import os
import pywgkey
import qrcode
import routeros_api
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from web.forms import *
from web.utils import DataMixin
from django.views.generic import ListView
from .models import *


class MikroTik:
    def __init__(self, name = 1):
        self.name = name
        self.connection()

    def get_all_options(self):
        return Settings.objects.all()[0]

    def connection(self):
        try:
            сonnection = routeros_api.RouterOsApiPool(
                host=self.get_all_options().Host,
                username=self.get_all_options().Username,
                password=self.get_all_options().Password,
                plaintext_login=True)
            self.api = сonnection.get_api()
            return True
        except:
            return False

    def get_server_public_key(self):
        return self.api.get_resource('/interface/wireguard').get(name=self.get_all_options().Interface)[0].get('public-key')

    def get_max_ip(self):
        list_get = self.api.get_resource(
            '/interface/wireguard/peers').get(interface=self.get_all_options().Interface)
        nums = [str(d['allowed-address']).split('.')[3] for d in list_get]
        max_ip = max([int(str(el[0:el.index('/')])) for el in nums])
        return max_ip + 1

    def create_client(self, form):
        get_client_name = self.api.get_resource(
            '/interface/wireguard/peers').get(comment=self.name)
        
        if get_client_name:
            return f'Client "{self.name}" already exists'
        else:
            self.client_key = pywgkey.WgKey()
            formating_network = (self.get_all_options().Network.split('/')[0])[:-1]
            self.new_ip = formating_network + \
                str(self.get_max_ip()) + '/' + (self.get_all_options().Network.split('/'))[1]
             
            ClientList.save_settings(form, self.client_key, self.new_ip)

            peers = self.api.get_resource('/interface/wireguard/peers')
            peers.add(interface=self.get_all_options().Interface,
                      comment=f"{self.name}",
                      public_key=self.client_key.pubkey,
                      allowed_address=self.new_ip,
                      persistent_keepalive='00:00:20')
            
            template = f"""
            [Interface]
            PrivateKey = {self.get_server_public_key()}
            Address = {self.new_ip}
            DNS = {self.get_all_options().DNS}
            MTU = {self.get_all_options().MTU}

            [Peer]
            PublicKey = {self.client_key.privkey}
            AllowedIPs = 0.0.0.0/0
            Endpoint = {self.get_all_options().Endpoint}
            PersistentKeepalive = 30
            """

            QR = qrcode.make(template)
            QR.save(f"web/QR/{self.name}.png")

            file = open(f"web/configs/{self.name}.conf", "w")
            file.write(template)
            file.close()

            return 'Client created'
        
    def delete_client(self):
        list_get = self.api.get_resource('/interface/wireguard/peers')
        get_id = list_get.get(comment=self.name)[0].get('id')
        list_get.remove(id=get_id)
        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   fr'configs\{self.name}.conf')
        QR_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               fr'QR\{self.name}.png')
        os.remove(config_path)
        os.remove(QR_path)
        model = ClientList.objects.get(name=self.name)
        model.delete()


# Page views \/
class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Вход пользователя")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')


@login_required(login_url=reverse_lazy('login'))
def dashboard(request):
    if Settings.objects.all():
        objects = ClientList.objects.all()
        settings_form = ConSettings(request.POST)
        create_client_form = AddClient(request.POST)

        if create_client_form.is_valid():
            name = create_client_form.cleaned_data.get('name')
            interaction = MikroTik(name)
            interaction.create_client(create_client_form)
            return redirect('home')
        
        if settings_form.is_valid():
            Settings.save_settings(settings_form)

        option = MikroTik().get_all_options()
        page_context = {'Allowed_addr': option.Network,
        'Hostname': option.Host, 'Login': option.Username,
        'Password': option.Password, 'DNS': option.DNS, 
        'MTU': option.MTU, 'Interface': option.Interface, 
        'Endpoint': option.Endpoint, 'objects': objects,
        'create_client_form': create_client_form, 'settings_form': settings_form}

        return render(request, 'index.html', page_context)
    else:
        return redirect('settings')

@login_required(login_url=reverse_lazy('login'))
def settings(request):
    settings_form = ConSettings(request.POST)
    if settings_form.is_valid():
        Settings.save_settings(settings_form)
        return redirect('home')
    page_context = {'settings_form': settings_form}
    return render(request, 'settings.html', context=page_context)


def logout_user(request):
    logout(request)
    return redirect('login')


def download(request, name):
    filename = fr"{os.path.dirname(os.path.dirname(__file__))}/web/configs/{name}.conf"
    response = FileResponse(open(filename, 'rb'))
    return response


def delete(request, name):
    interaction = MikroTik(name)
    interaction.delete_client()
    return redirect('home')
