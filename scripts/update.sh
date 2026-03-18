#!/bin/bash

# Script de mise à jour pour ORLYNE-A12B

echo "🔄 Mise à jour d'ORLYNE-A12B..."

# Sauvegarde avant mise à jour
./scripts/backup.sh

# Arrêt du service
./scripts/stop.sh

# Mise à jour du code
git pull

# Mise à jour des dépendances
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Mise à jour de la base de connaissances
python scripts/update_knowledge.py

# Redémarrage
./scripts/start.sh

echo "✅ Mise à jour terminée"