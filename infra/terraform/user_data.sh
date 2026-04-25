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
  git clone https://github.com/NewSwede/devops-production-app.git
fi

cd /home/ubuntu/devops-production-app

if [ ! -f ".env" ]; then
  cat <<'EOF' > .env
IMAGE_TAG=bootstrap
EOF
fi

docker-compose down || true
docker-compose up -d --build
