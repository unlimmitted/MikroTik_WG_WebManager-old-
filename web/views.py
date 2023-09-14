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
import re


class Validation:
    def __init__(self, form) -> None:
        self.host = form.cleaned_data.get('host')
        self.username = form.cleaned_data.get('username')
        self.password = form.cleaned_data.get('password')
        self.address = form.cleaned_data.get('client_address')
        self.local_network = form.cleaned_data.get('local_network')

    def check_connection(self):
        try:
            connect = routeros_api.RouterOsApiPool(
            host=self.host,
            username=self.username,
            password=self.password,
            plaintext_login=True)
            connect.get_api()
        except routeros_api.exceptions.RouterOsApiConnectionError:
            return 'Connection error, check the correctness of the data in the connection form'
        except routeros_api.exceptions.RouterOsApiCommunicationError as Error:
            return 'Authorization error, check the correctness of the data in the connection form'

    def validate_form_data(self):
        error = []
        if bool(re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{2}", self.address)) is False:
            error.append('Error, check the "Host" field is correct')
        if bool(re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{2}", self.local_network)) is False:
            error.append('Error, check that the "Local network" field is correct')
        return error

    def run(self):
        conn_error = self.check_connection()
        form_error = self.validate_form_data()
        if conn_error or form_error:
            return conn_error, form_error
        else:
            return None

class Configurator:
    def __init__(self ,options, settings_form):
        self.service_client_key = pywgkey.WgKey()

        # Connection properties
        self.host = settings_form.cleaned_data.get('host')
        self.username = settings_form.cleaned_data.get('username')
        self.password = settings_form.cleaned_data.get('password')
        # Server Interface properties
        self.server_interface_name = options.server_interface
        self.server_mtu = '1420'
        self.server_network = options.server_network
        self.server_listen_port = settings_form.cleaned_data.get('server_listen_port')
        # Client Interface properties
        self.client_interface_name = options.client_interface_name
        self.client_mtu = '1280'
        self.client_private_key = settings_form.cleaned_data.get('client_private_key')
        # Client Peer properties
        self.client_public_key = settings_form.cleaned_data.get('client_public_key')
        self.endpoint = settings_form.cleaned_data.get('client_endpoint')
        self.endpoint_port = settings_form.cleaned_data.get('client_endpoint_port')
        self.client_preshared_key = settings_form.cleaned_data.get('client_preshared_key')
        self.persistent_keep_alive = '00:00:20'
        # Other client properties
        self.client_address = settings_form.cleaned_data.get('client_address')

        self.local_network = settings_form.cleaned_data.get('local_network')

        self.connection()

    # Connect to MikroTik
    def connection(self):
        try:
            connect = routeros_api.RouterOsApiPool(
                host=self.host,
                username=self.username,
                password=self.password,
                plaintext_login=True)
            self.api = connect.get_api()
            return True
        except:
            return False

    def create_interfaces(self):
        interfaces = self.api.get_resource('/interface/wireguard')
        interfaces.add(
            name=self.server_interface_name,
            mtu=self.server_mtu,
            listen_port=str(self.server_listen_port))
        interfaces.add(
            name=self.client_interface_name,
            mtu=self.client_mtu,
            private_key=self.client_private_key)

    def create_client_peer(self):
        client_peer = self.api.get_resource('/interface/wireguard/peers')
        client_peer.add(
            interface=self.client_interface_name,
            public_key=self.client_public_key,
            endpoint_address=self.endpoint,
            endpoint_port=str(self.endpoint_port),
            allowed_address='0.0.0.0/0',
            preshared_key=self.client_preshared_key,
            persistent_keepalive=self.persistent_keep_alive
        )

    def create_service_server_peer(self):
        server_peer = self.api.get_resource('/interface/wireguard/peers')
        server_peer.add(
            interface=self.server_interface_name,
            public_key=self.service_client_key.pubkey,
            allowed_address='10.10.10.1',
            comment='service',
            persistent_keepalive=self.persistent_keep_alive
        )

    def create_routing_table(self):
        routing = self.api.get_resource('/routing/table')
        routing.add(
            disabled='no',
            fib='True',
            name='toVpn'
        )

    def create_ip_rules(self):
        ip_addresses = self.api.get_resource('/ip/address')
        # Server network
        ip_addresses.add(
            address='10.10.10.1/24',
            network='10.10.10.0',
            interface=self.server_interface_name
        )
        # Client
        ip_addresses.add(
            address=self.client_address,
            interface=self.client_interface_name
        )
        # Edit firewall
        firewall_address = self.api.get_resource('/ip/firewall/address-list/')
        firewall_address.add(
            list='ignoreVPN',
            address='10.10.10.0/24',
        )
        firewall_address.add(
            list='ignoreVPN',
            address=self.local_network
        )
        firewall_mangle = self.api.get_resource('/ip/firewall/mangle')
        firewall_mangle.add(
            action='mark-routing',
            chain='prerouting',
            dst_address_list='!ignoreVpn',
            in_interface=self.server_interface_name,
            new_routing_mark='toVpn',
            passthrough='no'
        )
        firewall_nat = self.api.get_resource('/ip/firewall/nat')
        firewall_nat.add(
            action='masquerade',
            chain='srcnat',
            out_interface=self.client_interface_name
        )
        firewall_nat.add(
            action='masquerade',
            chain='srcnat',
            out_interface=self.server_interface_name

        )
        firewall_service_port = self.api.get_resource('/ip/firewall/')
        firewall_service_port.call('service-port/enable', {'numbers': 'irc'})
        firewall_service_port.call('service-port/enable', {'numbers': 'rtsp'})
        # IP Routes
        routes = self.api.get_resource('/ip/route')
        numbers = self.local_network.split('/')[0].split('.')
        gateway = f'{numbers[0]}.{numbers[1]}.{numbers[2]}.1'
        routes.add(
            distance='1',
            dst_address='0.0.0.0/0',
            gateway=rf"{gateway}",
            routing_table='main',
            scope='30',
            suppress_hw_offload='no',
            target_scope='10',
            vrf_interface=self.server_interface_name

        )
        routes.add(
            distance='1',
            dst_address='0.0.0.0/0',
            gateway=self.client_interface_name,
            routing_table='toVpn',
            scope='30',
            suppress_hw_offload='no',
            target_scope='10',
        )

    def run(self):
        self.create_interfaces()
        self.create_client_peer()
        self.create_service_server_peer()
        self.create_routing_table()
        self.create_ip_rules()


class MikroTik:
    def __init__(self, name=1):
        self.name = name
        self.connection()

    def get_all_options(self):
        return Settings.objects.all()[0]

    def connection(self):
        сonnection = routeros_api.RouterOsApiPool(
            host=self.get_all_options().host,
            username=self.get_all_options().username,
            password=self.get_all_options().password,
            plaintext_login=True)
        self.api = сonnection.get_api()
        return self.api

    def get_server_public_key(self):
        return self.api.get_resource('/interface/wireguard').get(name=self.get_all_options().server_interface)[0].get('public-key')

    def get_max_ip(self):
        list_get = self.api.get_resource(
            '/interface/wireguard/peers').get(interface=self.get_all_options().server_interface)
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
            wg_network = self.get_all_options().server_network
            formating_network = (wg_network.split('/')[0])[:-1]
            self.new_ip = formating_network + str(self.get_max_ip()) + '/' + \
                (wg_network.split('/'))[1]

            ClientList.save_settings(form, self.client_key, self.new_ip)

            peers = self.api.get_resource('/interface/wireguard/peers')
            peers.add(
                interface=self.get_all_options().server_interface,
                comment=f"{self.name}",
                public_key=self.client_key.pubkey,
                allowed_address=self.new_ip,
                persistent_keepalive='00:00:20')

            template = f"""
            [Interface]
            PrivateKey = {self.client_key.privkey}
            Address = {self.new_ip}
            DNS = 1.1.1.1
            MTU = 1400

            [Peer]
            PublicKey = {self.get_server_public_key()}
            AllowedIPs = 0.0.0.0/0
            Endpoint = {self.get_all_options().server_endpoint + ':'
                        + str(self.get_all_options().server_listen_port)}
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
        model = ClientList.objects.get(Name=self.name)
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
        create_client_form = AddClient(request.POST)
        objects = ClientList.objects.all()
        page_context = {'create_client_form': create_client_form, 'objects': objects}
        if create_client_form.is_valid():
            name = create_client_form.cleaned_data.get('Name')
            interaction = MikroTik(name)
            page_context = {'create_client_form': create_client_form, 'objects': objects,
                             'feedback': interaction.create_client(create_client_form)}
            return render(request, 'index.html', page_context)

        
        return render(request, 'index.html', page_context)
    else:
        return redirect('settings')


@login_required(login_url=reverse_lazy('login'))
def settings(request):
    settings_form = MTSettings(request.POST)
    page_context = {'settings_form': settings_form}
    if settings_form.is_valid():
        check = Validation(settings_form)
        errors = check.run()
        if errors is None:
            Settings.save_settings(settings_form)
            options = Settings.objects.all()[0]
            configurator = Configurator(options ,settings_form)
            configurator.run()
            return redirect('home')
        else:
            page_context = {'settings_form': settings_form, 'conn_error': errors[0], 'form_error': errors[1]}
            return render(request, 'settings.html', context=page_context)
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
