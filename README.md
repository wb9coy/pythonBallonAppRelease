# pythonBallonAppRelease
Arizona Near Space Research RPI based payload.   Sends still pics to the ground and records video on the sd card

NAME="Debian GNU/Linux"
VERSION_ID="11"
VERSION="11 (bullseye)"
VERSION_CODENAME=bullseye

sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
CONF_SWAPSIZE=2048
save
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

sudo apt update
sudo apt full-upgrade
sudo reboot

sudo nano /boot/config.txt
force_turbo=1
over_voltage=4
save
sudo reboot


Raspberry PI config
	SSH on
	SPI on
        I2C on
        serial port on
        serial console off

sudo pip install libscrc
sudo pip install smbus2
sudo pip install RPI.BME280

To run at start refer to systemd/README

Seup RTC
--------
In the tools dir execute rtc


Set as AP
---------
Getting started
In order to work as an access point, the Raspberry Pi will need to have access point software installed, along with DHCP server software to provide connecting devices with a network address.

To create an access point, we’ll need DNSMasq and HostAPD. Install all the required software in one go with this command:

sudo apt install dnsmasq hostapd
Since the configuration files are not ready yet, we need to stop the new software from running:

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
Configure a static IP
We are configuring a standalone network to act as a server, so the Raspberry Pi needs to have a static IP address assigned to the wireless port. Here I assume we are using the standard 192.168.x.x IP addresses for our wireless network, so we will assign the server the IP address 192.168.4.1.

To configure the static IP address, edit the dhcpcd configuration file with:

sudo nano /etc/dhcpcd.conf
Go to the end of the file and edit it so that it looks like the following:

interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
Now restart the dhcpcd daemon and set up the new wlan0 configuration:

sudo service dhcpcd restart
Configure the DHCP server
The DHCP service is provided by dnsmasq. Let’s backup the old configuration file and then create a new one:

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo nano /etc/dnsmasq.conf
Type the following information into the dnsmasq configuration file and save it:

interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
This will provide IP-addresses between 192.168.4.2 and 192.168.4.20 with a lease time of 24 hours. Now start dnsmasq to use the updated configuration:

sudo systemctl start dnsmasq
Configure the access point host software
Now it is time to configure the access point software:

sudo nano /etc/hostapd/hostapd.conf
Add the below information to the configuration file:

interface=wlan0
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
ssid=payload
wpa_passphrase=123456789


Make sure to change the ssid and wpa_passphrase. We now need to tell the system where to find this configuration file. Open the hostapd file:

sudo nano /etc/default/hostapd
Find the line with #DAEMON_CONF, and replace it with this:

DAEMON_CONF="/etc/hostapd/hostapd.conf"
Start up the wireless access point
Run the following commands to enable and start hostapd:

sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
Enable routing and IP masquerading
You may want devices connected to your wireless access point to access the main network and from there the internet. To do so, we need to set up routing and IP masquerading on the Raspberry Pi. We do this by editing the sysctl.conf file:

sudo nano /etc/sysctl.conf
And uncomment the following line:

net.ipv4.ip_forward=1
Next we need a “masquerade” firewall rule such that the IP-addresses of the wireless clients connected to the Raspberry Pi can be substituted by their own IP address on the local area network. To do so enter:

sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
Now to save these firewall rules and automatically use them upon boot, we will use the netfilter-persistent service:

sudo netfilter-persistent save
Once rebooted, if you go to another device that has wireless and search for wireless networks you should be able to see your wireless access point and be able to connect to it using the credentials that you configured.

Stop the access point
First stop the hostadp service:

sudo systemctl stop hostap
Edit the dhcpcd.conf file:

sudo nano /etc/dhcpcd.conf
and comment out the lines related to the static IP address. Now reboot

sudo reboot
