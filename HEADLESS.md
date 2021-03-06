# Headless install of Raspberry Pi Zero W

These instructions show how to start up a new Pi Zero W with PiOLED display running without connecting a monitor or keyboard to the Pi.

Since the Pi Zero W has micro-HDMI and micro-USB connectors, it's much easier to put the information for your wireless network on the boot volume and SSH to the Pi to configure it. The instructions for doing this are here:

https://learn.adafruit.com/raspberry-pi-zero-creation/overview

Summary:
- Use Etcher to burn the Raspbian Stretch image on the micro-SD card. You do not have to unzip the file when using Etcher.
- Mount the SD card to a computer
- Create a file named `wpa_supplicant.conf` with the details of your wifi network (see file format below).
- Edit the `config.txt` file to enable the UART for troubleshooting (I didn't do this).
- Add an empty file named `ssh` to the boot volume. SSH is not enabled by default on later versions of Raspbian.
- Install the micro-SD card into your Pi and power it on. It should automatically attach to your wifi network.

This is the format of the `wpa_supplicant.conf` file for **Raspbian Stretch**.

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOURSSID"
    psk="YOURPASSWORD"
    scan_ssid=1
}
```

## First boot

You should change the default password for the `pi` account or create a new user account. I also used `sudo raspi-config` to set my timezone and change the hostname. Use the following commands to update Raspbian:

```
sudo apt-get update
sudo apt-get dist-upgrade
```

## Preparing for the OLED screen

Prior to installing the OLED Bonnet, run the following commands on the Pi as described at https://learn.adafruit.com/adafruit-128x64-oled-bonnet-for-raspberry-pi/usage

```python
sudo apt-get update
sudo apt-get install build-essential python-dev python-pip
sudo pip install RPi.GPIO
sudo apt-get install python-imaging python-smbus
sudo apt-get install git
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python setup.py install
# get I2C bus ready
sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tools
# under "interfacing options" enable I2C
sudo raspi-config
```

Now you can install the screen and run `sudo i2cdetect -y 1` to see the display listed (probably at address `3c`).