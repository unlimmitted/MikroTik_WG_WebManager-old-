# WireGuard on MikroTik Web Manager

New: https://github.com/unlimmitted/MTWireGuardEasy

## Description
![image](https://github.com/unlimmitted/MikroTik_WG_WebManager/assets/108941648/bd087803-ebe6-4625-9b91-42f7c6e48cf2)
__Software that will help you bypass VPN WireGuard blocking by mobile operators in Russia.__

To work, you need a virtual machine (or any other option) with a WireGuard server outside Russia. You will need to create 1 config file, it is required to configure the MikroTik virtual machine (more details in the [configuration section](#configurate-mikrotik)).


## Install
__Guide on how to screw up mobile operators in Russia :)__

This section describes in detail the installation and configuration process

### StarUp
Copy repository
```cpp
git clone https://github.com/unlimmitted/MikroTik_WG_WebManager.git
```

__Run in ~/MikroTik_WG_WebManager__
```cpp
sudo docker-compose build
```
```cpp
sudo docker-compose up -d
```

Now the web interface is available at http://0.0.0.0:8000

__Login:__ admin 

__Password:__ admin

### Configurate MikroTik
Before going to the web interface, connect to MikroTik using __WinBox__ and enable __DHCP Client__ to get the __IP Address__ which you will need later.

![image-3](https://github.com/unlimmitted/MikroTik_WG_WebManager/assets/108941648/b3045dc5-69b7-49fd-be7f-c913ce903584)![image-4](https://github.com/unlimmitted/MikroTik_WG_WebManager/assets/108941648/ffcdaa57-eca4-4aec-95a5-348246cb06a1)

Before starting the setup, create a config file on the remote machine with WireGuard and open it in Notepad (or any other text editor)

Now open the web interface (you will be automatically redirected to the configuration page)

![image-2](https://github.com/unlimmitted/MikroTik_WG_WebManager/assets/108941648/60d3fd0b-cb34-49f3-a8d0-6c4fb0fc0b38)

__Connection__
Here is the information required to connect to your Mikrotik (it is recommended to use a virtual machine)
_Example_
* Host - 172.21.0.1
* Username - admin
* Password - Qwerty12345

__WireGuard in VPN__
Here you need to specify the parameters for VPN in Mikrotik
* Listen port - The port on which clients will connect (For example: 51820)
* Endpoint - Your IP or Hostname

__WireGuard out to VPN__
Here you will need your external WireGuard config
__*All fields are specified in accordance with the order in which they appear in the config file*__
Simply transfer the settings from the configuration file to the appropriate fields in the form section

__Other__
* Local network - Your local network (For example: 192.168.0.0/24)


__After filling in all fields, click the Save button. MikroTik will automatically configure itself and redirect you to the main web interface page__

## Use
![image-1](https://github.com/unlimmitted/MikroTik_WG_WebManager/assets/108941648/beb3d58d-9211-4107-9d56-ad48ed34d117)

To create a new client, simply enter __any name__ in the form and click the __Create button.__

After that, the created client will appear in the list on the left by clicking on which you will be able to scan the QR code and download the config file
