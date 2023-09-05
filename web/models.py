from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class ClientList(models.Model):
    name = models.CharField(max_length=35, verbose_name='name')
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
            add_client_info.Endpoint = settings.Endpoint
            add_client_info.DNS = settings.DNS
            add_client_info.MTU = settings.MTU
            add_client_info.Address = ip
            add_client_info.AllowedIPs = '0.0.0.0/0'
            add_client_info.PrivateKey = str(client_key.privkey)
            add_client_info.PublicKey = str(client_key.pubkey)
            add_client_info.PersistentKeepalive = '30'
            add_client_info.save()

class Settings(models.Model):
    Host = models.CharField(max_length=40, verbose_name='Host')
    Username = models.CharField(max_length=255, verbose_name='Username')
    Password = models.CharField(max_length=255, verbose_name='Password')
    Endpoint = models.CharField(max_length=40, verbose_name='Endpoint')
    Network = models.CharField(max_length=40, verbose_name='Network')
    Interface = models.CharField(max_length=15, verbose_name='Interface')
    MTU = models.CharField(max_length=6, verbose_name='MTU')
    DNS = models.CharField(max_length=40, verbose_name='DNS')

    def save_p(self, *args, **kwargs):
        self.Password = make_password(self.Password)
        super(Settings, self).save(*args, **kwargs)

    @staticmethod
    def save_settings(form):
        settings = Settings.objects.all()
        if settings:
            property = Settings.objects.filter(Host=settings[0].Host).update(
                Host = form.cleaned_data.get('Host'),
                Username = form.cleaned_data.get('Username'),
                Password = form.cleaned_data.get('Password'),
                Endpoint = form.cleaned_data.get('Endpoint'),
                Network = form.cleaned_data.get('Network'),
                Interface = form.cleaned_data.get('Interface'),
                MTU = form.cleaned_data.get('MTU'),
                DNS = form.cleaned_data.get('DNS')
            )
        else:
            if form.is_valid():
                property = form.save(commit=False)
                property.Host = form.cleaned_data.get('Host')
                property.Username = form.cleaned_data.get('Username')
                property.Password = form.cleaned_data.get('Password')
                property.Endpoint = form.cleaned_data.get('Endpoint')
                property.Network = form.cleaned_data.get('Network')
                property.Interface = form.cleaned_data.get('Interface')
                property.MTU = form.cleaned_data.get('MTU')
                property.DNS = form.cleaned_data.get('DNS')
                property.save()
