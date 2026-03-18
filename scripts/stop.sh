#!/bin/bash

# Script d'arrêt pour ORLYNE-A12B

echo "🛑 Arrêt d'ORLYNE-A12B..."

# Arrêt du processus Python
pkill -f "python -m src.main"

# Arrêt des conteneurs Docker
docker-compose down 2>/dev/null

echo "✅ Orlyne arrêté"