#!/bin/bash

systemctl disable massa-monitoring
systemctl stop massa-monitoring
# Installing docker-compose

sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
echo -ne '\n' | sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo "$UBUNTU_CODENAME") stable"
sudo apt update
sudo apt install -y docker-ce docker-compose
usermod -aG docker $USER

echo "Enter master server ip ( EXAMPLE: 127.0.0.1 )"
read MASTER_SERVER_IP

if [ -z "$MASTER_SERVER_IP" ]
then
  MASTER_SERVER_IP="127.0.0.1"
fi

echo "[INFO] MASTER_SERVER_IP set $MASTER_SERVER_IP"

PASSWORD=$(cat /dev/urandom | tr -dc '[:alpha:]' | fold -w ${1:-20} | head -n 1)
echo "POSTGRES_USER=db_user
POSTGRES_DB=db
POSTGRES_PASSWORD=$PASSWORD" > ./.env/vars

echo "PG_HOST='127.0.0.1'
PG_PORT='5434'
POSTGRES_USER='db_user'
POSTGRES_DB='db'
POSTGRES_PASSWORD='$PASSWORD'
MASTER_SERVER_IP='$MASTER_SERVER_IP'" > ./app/settings.py

echo "[INFO] Starting node explorer..."
docker-compose up -d --build
echo "[INFO] Node explorer is up!"

sudo apt install -y python3-pip

echo "[Unit]
Description=Massa monitoring
After=online.target

[Service]
#Type=root
User=root
Environment=
ExecStart=/usr/bin/python3 /root/MassaNodeViewer/manage.py
Restart=on-failure
RestartSec=3
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/massa-monitoring.service

python3 -m pip install -r ./requirements.txt
systemctl enable massa-monitoring --now

IP=$(curl ifconfig.co)
echo "[INFO] Firewall reloaded seccessful! Checking info on http://$IP:10100/metrics"
echo "[INFO] You can change any settings in settings.env file."
echo "[INFO] For apply your changes execute docker-compose up -d --build"
