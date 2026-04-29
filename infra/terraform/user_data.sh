#!/bin/bash
set -euo pipefail

exec > >(tee /var/log/devops-app-bootstrap.log) 2>&1

apt update -y
apt upgrade -y
apt install -y curl docker.io git

mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL \
  https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

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

docker compose -f docker-compose.dev.yml down || true
docker compose -f docker-compose.dev.yml up -d --build
