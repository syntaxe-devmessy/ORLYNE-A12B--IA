# ORLYNE-A12B - Guide de déploiement sur VPS

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen)

Créée par **Syntaxe Tech**

## 📋 Table des matières
- [Prérequis VPS](#prérequis-vps)
- [Installation rapide](#installation-rapide)
- [Configuration Docker](#configuration-docker)
- [Configuration domaine avec Nginx](#configuration-domaine-avec-nginx)
- [SSL Let's Encrypt](#ssl-lets-encrypt)
- [Gestion des services](#gestion-des-services)
- [Monitoring](#monitoring)
- [Sauvegarde](#sauvegarde)
- [Dépannage](#dépannage)
- [Sécurité](#sécurité)

## 🖥️ Prérequis VPS

### Spécifications minimales
| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| CPU | 4 cœurs | 8+ cœurs |
| RAM | 16 GB | 32 GB |
| Stockage | 50 GB SSD | 100 GB SSD |
| GPU | Optionnel | NVIDIA 16GB+ |
| OS | Ubuntu 22.04 | Ubuntu 22.04 |

### Installation des prérequis
```bash
# Connexion au VPS
ssh root@IP_DE_VOTRE_VPS

# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installation Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Vérification
docker --version
docker-compose --version

# Redémarrage pour prendre les changements
sudo reboot


# ORLYNE-A12B - Déploiement sur VPS

1. Prérequis VPS

· Ubuntu 22.04
· 4 CPU / 16GB RAM minimum
· Docker et Docker Compose

2. Installation rapide

```bash
# Connexion au VPS
ssh root@IP_DE_VOTRE_VPS

# Installation Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Installation Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Redémarrer
sudo reboot
```

3. Installation Orlyne

```bash
# Après reboot
cd /opt
sudo mkdir orlyne
sudo chown $USER:$USER orlyne
git clone https://github.com/syntaxetech/ORLYNE-A12B.git orlyne
cd orlyne

# Configuration
cp .env.example .env
nano .env
# Modifier au moins SECRET_KEY et POSTGRES_PASSWORD

# Lancement
cd docker
docker-compose up -d

# Vérification
docker-compose ps
```

4. Configuration domaine (Optionnel)

```bash
# Installer Nginx
sudo apt install nginx -y

# Configurer le site
sudo nano /etc/nginx/sites-available/orlyne
```

```nginx
server {
    listen 80;
    server_name votredomaine.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Activation
sudo ln -s /etc/nginx/sites-available/orlyne /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

5. SSL Let's Encrypt (Optionnel)

```bash
# Installation Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtenir certificat
sudo certbot --nginx -d votredomaine.com
```

6. Commandes utiles

```bash
# Voir les logs
docker-compose logs -f orlyne

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Statut des conteneurs
docker-compose ps
```

7. Accès

· Interface web: http://votredomaine.com ou http://IP_VPS:8000
· API: http://votredomaine.com/api
· Documentation API: http://votredomaine.com/docs

8. Vérification

```bash
curl http://localhost:8000/health
# Réponse: {"status":"healthy"}
```

---

Installation terminée ! 🚀