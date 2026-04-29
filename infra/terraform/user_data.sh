#!/bin/bash
set -euo pipefail

exec > >(tee /var/log/devops-app-bootstrap.log) 2>&1

apt update -y
apt upgrade -y
apt install -y docker.io docker-compose git

systemctl enable --now docker
usermod -aG docker ubuntu

cd /home/ubuntu

if [ ! -d "devops-production-app" ]; then
  sudo -u ubuntu git clone https://github.com/NewSwede/devops-production-app.git
fi

cd /home/ubuntu/devops-production-app
chown -R ubuntu:ubuntu /home/ubuntu/devops-production-app

if [ ! -f ".env" ]; then
  cat <<'EOF' > .env
IMAGE_TAG=local
POSTGRES_DB=devdb
POSTGRES_USER=devuser
POSTGRES_PASSWORD=devpass
EOF
  chown ubuntu:ubuntu .env
  chmod 600 .env
fi

docker-compose -f docker-compose.dev.yml down || true
docker-compose -f docker-compose.dev.yml up -d --build
