from django.db import models
import routeros_api
# Create your models here.
class ClientList(models.Model):
    Name = models.CharField(max_length=35, verbose_name='Name')
    PrivateKey = models.CharField(max_length=255, verbose_name='PrivateKey')
    PublicKey = models.CharField(max_length=255, verbose_name='PublicKey')
    Address = models.CharField(max_length=255, verbose_name='Address')
    DNS = models.CharField(max_length=255, verbose_name='DNS')
    MTU = models.CharField(max_length=255, verbose_name='MTU')
    AllowedIPs = models.CharField(max_length=255, verbose_name='AllowedIPs')
    Endpoint = models.CharField(max_length=255, verbose_name='Endpoint')
    PersistentKeepalive = models.CharField(
        max_length=255, verbose_name='PersistentKeepalive')
    
    @staticmethod
    def save_settings(form, client_key, ip):
        settings = Settings.objects.all()[0]
        if form.is_valid():
            add_client_info = form.save(commit=False)
            add_client_info.Endpoint = settings.server_endpoint + ':' + settings.server_listen_port
            add_client_info.DNS = '1.1.1.1'
            add_client_info.MTU = '1400'
            add_client_info.Address = ip
            add_client_info.AllowedIPs = '0.0.0.0/0'
            add_client_info.PrivateKey = str(client_key.privkey)
            add_client_info.PublicKey = str(client_key.pubkey)
            add_client_info.PersistentKeepalive = '30'
            add_client_info.save()

class Settings(models.Model):
    # Connection properties
    host = models.CharField(max_length=40, verbose_name='Host')
    username = models.CharField(max_length=255, verbose_name='Username')
    password = models.CharField(max_length=255, verbose_name='Password')
    # WG server properties
    server_interface = models.CharField(max_length=15, verbose_name='server_interface')
    server_listen_port = models.CharField(max_length=10, verbose_name='server_listen_port')
    # Server peers properties
    server_endpoint = models.CharField(max_length=40, verbose_name='server_endpoint')
    server_endpoint_port = models.CharField(max_length=10, verbose_name='server_endpoint_port') 
    server_network = models.CharField(max_length=40, verbose_name='server_network')
    # Client interface
    client_interface_name = models.CharField(max_length=25, verbose_name='client_interface_name')
    client_private_key = models.CharField(max_length=150, verbose_name='client_private_key')
    # Client peer
    client_public_key = models.CharField(max_length=150, verbose_name='client_public_key')
    client_endpoint = models.CharField(max_length=40, verbose_name='client_endpoint')
    client_endpoint_port = models.CharField(max_length=10, verbose_name='client_endpoint_port')
    client_preshared_key = models.CharField(max_length=150, verbose_name='client_preshared_key')
    client_address = models.CharField(max_length=40, verbose_name='client_address')
    # Other properties
    local_network = models.CharField(max_length=40, verbose_name='local_network')

    @staticmethod
    def check_connection(form):
        try:
            connect = routeros_api.RouterOsApiPool(
            host=form.cleaned_data.get('host'),
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password'),
            plaintext_login=True)
            con = connect.get_api()
            return True
        except routeros_api.exceptions.RouterOsApiCommunicationError as Error:
            return Error


    @staticmethod
    def save_settings(form):
        # settings = Settings.objects.all()
        # if settings:
        #     Settings.objects.filter(host=settings[0].host).update(
        #         host = form.cleaned_data.get('host'),
        #         username = form.cleaned_data.get('username'),
        #         password = form.cleaned_data.get('password'),

        #         server_interface = form.cleaned_data.get('server_interface'),
        #         server_listen_port = form.cleaned_data.get('server_listen_port'),
        #         server_endpoint = form.cleaned_data.get('server_endpoint'),
        #         server_endpoint_port = form.cleaned_data.get('server_endpoint_port'),

        #         server_network = form.cleaned_data.get('server_network'),

        #         client_interface_name = form.cleaned_data.get('client_interface_name'),
        #         client_private_key = form.cleaned_data.get('client_private_key'),

        #         client_public_key = form.cleaned_data.get('client_public_key'),
        #         client_endpoint = form.cleaned_data.get('client_endpoint'),
        #         client_endpoint_port = form.cleaned_data.get('client_endpoint_port'),
        #         client_preshared_key = form.cleaned_data.get('client_preshared_key'),
        #         client_address = form.cleaned_data.get('client_address'),

        #         local_network = form.cleaned_data.get('local_network')
        #     )
        # else:
        if form.is_valid():
            property = form.save(commit=False)
            property.server_interface = 'wg-in'
            property.client_interface_name = 'wg-outToVpn'
            property.server_network = '10.10.10.0/32'
            property.save()
