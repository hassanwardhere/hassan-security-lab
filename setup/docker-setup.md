# Docker and Portainer Setup

## Overview
Docker provides the containerisation engine for all tools in this lab.
Portainer provides a visual management interface for all containers.
All container data is stored on the 1TB HDD mounted at /mnt/hdd.

---

## Step 1 — Install Docker

### Commands Run
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg \
  --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

### Add User to Docker Group
```bash
sudo usermod -aG docker $USER
newgrp docker
docker --version && docker compose version
```

### Result

| Component       | Version  |
|-----------------|----------|
| Docker Engine   | 29.3.1   |
| Docker Compose  | v5.1.1   |

![Docker Installation](screenshots/DOCKER%20INSTALLED.png)

---

## Step 2 — Prepare HDD Storage for Docker Data

All container data stored on 1TB HDD to preserve SSD lifespan.
```bash
sudo mkdir -p /mnt/hdd/docker
sudo chown -R $USER:docker /mnt/hdd/docker
```

---

## Step 3 — Install Portainer
```bash
docker volume create portainer_data

docker run -d \
  -p 8000:8000 \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

### Access Portainer
Open browser on any device on the same network and go to:
https://[homelab-ip]:9443


> **Note:** Replace `<homelab-ip>` with the local IP address 
> of your home lab machine. In this lab that is a private 
> network address accessible only on the local network.

## Verification

- [x] Docker installed and running
- [x] User added to Docker group
- [x] Portainer container running
- [x] Portainer accessible via browser

---

## Notes
- Docker service starts automatically on boot
- Portainer persists data in a named Docker volume