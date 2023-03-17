import json
import os

import pywgkey
import qrcode
import routeros_api
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from web.forms import *
from web.utils import DataMixin


# Create your views here.


def connection():
    with open('settings.json') as json_file:
        data = json.load(json_file)
        for p in data['settings']:
            address = p['address']
            login = p['login']
            password = p['password']
    сonnection = routeros_api.RouterOsApiPool(
        host=address,
        username=login,
        password=password,
        plaintext_login=True
    )
    api = сonnection.get_api()
    return api


def get_server_public_key(api):
    return api.get_resource('/interface/wireguard').get(name="wg-in")[0].get('public-key')


def get_interface_from_settings():
    with open('settings.json') as settings:
        data = json.load(settings)
        for p in data['settings']:
            interface = p['Interface']
        return interface


def get_max_ip(api):
    list_get = api.get_resource('/interface/wireguard/peers').get(interface=get_interface_from_settings())
    nums = [str(d['allowed-address']).split('.')[3] for d in list_get]
    max_ip = max([int(str(el[0:el.index('/')])) for el in nums])
    return max_ip + 1


def create_conf(public_key, ip, client_private_key, end_point, dns, MTU, comment):
    template = f"""
    [Interface]
    PrivateKey = {client_private_key}
    Address = {ip}
    DNS = {dns}
    MTU = {MTU}

    [Peer]
    PublicKey = {public_key}
    AllowedIPs = 0.0.0.0/0
    Endpoint = {end_point}
    PersistentKeepalive = 30
    """
    QR = qrcode.make(template)
    QR.save(f"web/QR/{comment}.png")
    file = open(f"web/configs/{comment}.conf", "w")
    file.write(template)
    file.close()


## Page views \/


def dashboard(request):
    form = ClientList.objects.all()
    return render(request, 'index.html', context={'form': form})


def settings(request):
    form = ConSettings(request.POST)
    if form.is_valid():
        data_check = form.cleaned_data.get('Interface')
        if data_check:
            form_data = form.cleaned_data
            data = {'settings': []}
            data['settings'].append({
                'end_point': form_data.get('Endpoint'),
                'network': form_data.get('Allowed_addr'),
                'MTU': form_data.get('MTU'),
                'DNS': form_data.get('DNS'),
                'Interface': form_data.get('Interface'),
                'address': form_data.get('Hostname'),
                'login': form_data.get('Login'),
                'password': form_data.get('Password')
            })
            with open('settings.json', 'w') as outfile:
                json.dump(data, outfile, indent=2)
            return redirect('home')
        else:
            return render(request, 'settings.html', context={'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')


def showQR(request, name):
    return render(request, 'showQR.html', context={'name': name})


def download(request, name):
    filename = fr"{os.path.dirname(os.path.dirname(__file__))}/web/configs/{name}.conf"
    response = FileResponse(open(filename, 'rb'))
    return response


def delete(request, name):
    api = connection()
    list_get = api.get_resource('/interface/wireguard/peers')
    get_id = list_get.get(comment=name)[0].get('id')
    list_get.remove(id=get_id)
    config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                               fr'configs\{name}.conf')
    QR_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           fr'QR\{name}.png')
    os.remove(config_path)
    os.remove(QR_path)
    form = ClientList.objects.get(name=name)
    form.delete()
    return redirect('home')


def create_client(request):
    form = AddClient(request.POST)
    if form.is_valid():
        api = connection()
        client_data = form.save(commit=False)
        client_key = pywgkey.WgKey()
        with open('settings.json') as json_file:
            data = json.load(json_file)
            for p in data['settings']:
                network = p['network']
        formating_network = (network.split('/')[0])[:-1]
        new_ip = formating_network + str(get_max_ip(api)) + '/' + (network.split('/'))[1]
        with open('settings.json') as settings:
            list_address_num = api.get_resource('/interface/wireguard/peers')
            data = json.load(settings)
            for p in data['settings']:
                client_data.DNS = p['DNS']
                client_data.Endpoint = p['end_point']
                client_data.MTU = p['MTU']
            client_data.Address = new_ip
            client_data.AllowedIPs = '0.0.0.0/0'
            name = form.cleaned_data.get('name')
            client_data.PrivateKey = str(client_key.privkey)
            client_data.PublicKey = str(client_key.pubkey)
            client_data.PersistentKeepalive = '30'
            client_data.save()
        get_client_name = api.get_resource('/interface/wireguard/peers').get(comment=name)
        if get_client_name:
            return redirect('home')
        else:
            list_address_num.add(interface=get_interface_from_settings(),
                                 comment=f"{name}",
                                 public_key=client_key.pubkey,
                                 allowed_address=new_ip,
                                 persistent_keepalive='00:00:20')
            with open('settings.json') as settings:
                data = json.load(settings)
                for p in data['settings']:
                    end_point = p['end_point']
                    dns = p['DNS']
                    mtu = p['MTU']
            create_conf(get_server_public_key(api), new_ip, client_key.privkey, end_point, dns, mtu, name)
        return redirect('home')
    return render(request, 'createConfig.html', context={'form': form})


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Вход пользователя")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')
