#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root, use sudo "$0" instead" 1>&2
   exit 1
fi

cd /tmp

echo "Updating packages"
apt update
apt -y upgrade

echo "Installing dependancies"

apt -y install python python-dev python-pip libreadline-dev libzip-dev libcurl4-openssl-dev libssl-dev libxml2-dev libusb-1.0-0-dev libusb-1.0-0 automake autotools-dev autoconf checkinstall git libatlas-base-dev libjpeg-dev zlib1g-dev libtool libtool-bin m4 libplist-dev libusbmuxd-dev libimobiledevice-dev libffi-dev usbmuxd libfreetype6-dev

echo "Installing Python modules"
pip --no-cache-dir install setuptools wheel
pip wheel numpy
pip install numpy
pip --no-cache-dir install spidev libusb Pillow sh RPi.GPIO

echo "Setting up environment"

mkdir /var/lib/bananapi
echo "BOARD=bpi-m2z" >> /var/lib/bananapi/board.sh
echo "BOARD_AUTO=bpi-m2z" >> /var/lib/bananapi/board.sh
echo "BOARD_OLD=bpi-m64" >> /var/lib/bananapi/board.sh

echo "Enabling SPI"

echo "overlays=spi-spidev" >> /boot/armbianEnv.txt
echo "param_spidev_spi_bus=0" >> /boot/armbianEnv.txt

echo "Setting up GPIO & WiringPi"

git clone https://github.com/BPI-SINOVOIP/RPi.GPIO
cd RPi.GPIO
python setup.py install
cd ..

git clone https://github.com/BPI-SINOVOIP/BPI-WiringPi2
cd BPI-WiringPi2
chmod +x build
./build
cd ..

echo "Installing libimobiledevice"

git clone https://github.com/libimobiledevice/libplist
cd libplist
./autogen.sh
make
make install
cd ..

git clone https://github.com/libimobiledevice/libusbmuxd
cd libusbmuxd
./autogen.sh
make
sudo make install
cd ..

git clone https://github.com/libimobiledevice/libimobiledevice
cd libimobiledevice
./autogen.sh
make
make install
cd ..

git clone https://github.com/libimobiledevice/libirecovery
cd libirecovery
./autogen.sh
make
make install
cd ..

git clone https://github.com/libimobiledevice/idevicerestore
cd idevicerestore
./autogen.sh
make
make install
cd ..

rm -R /tmp/*

echo "Installing checkra1n"
wget https://assets.checkra.in/downloads/linux/cli/arm/dde0ee4255403a427636bb76e09e409487f8be128af4b7d89fac78548bd5b35a/checkra1n
chmod +x checkra1n
mv checkra1n /usr/local/bin/

sudo -u#1000 pip uninstall RPi.GPIO

cd /usr/local/share
git clone https://github.com/neomatrix125/ra1nman
cd ra1nman
chmod +x run.sh
cp ra1nman.service /etc/systemd/system/ && systemctl enable ra1nman.service

sleep 1

sudo reboot
