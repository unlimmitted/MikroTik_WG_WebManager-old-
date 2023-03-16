from django.db import models

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
    PersistentKeepalive = models.CharField(max_length=255, verbose_name='PersistentKeepalive')