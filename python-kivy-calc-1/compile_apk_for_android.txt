#if not working app store in ubuntu 20.04.02
sudo snap remove snap-store
sudo snap install snap-store

#before install pycharm
sudo apt -y install python3-distutils
sudo apt -y install python3-pip
pip3 install setuptools

sudo apt install -y git
git clone https://github.com/kivy/buildozer.git
cd buildozer
sudo python3 setup.py install

buildozer init

nano buildozer.spec

#https://buildozer.readthedocs.io/en/latest/installation.html#targeting-android
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade Cython==0.29.19 virtualenv  # the --user should be removed if you do this in a venv

# add the following line at the end of your ~/.bashrc file
export PATH=$PATH:~/.local/bin/

buildozer android debug deploy run
