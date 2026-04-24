#!/bin/bash
set -e

apt update -y
apt upgrade -y

apt install -y docker.io docker-compose git

systemctl start docker
systemctl enable docker

usermod -aG docker ubuntu

cd /home/ubuntu

if [ ! -d "devops-production-app" ]; then
  git clone https://github.com/NewSwede/devops-production-app.git
fi

cd devops-production-app

if [ ! -f ".env" ]; then
  echo "IMAGE_TAG=bootstrap" > .env
fi