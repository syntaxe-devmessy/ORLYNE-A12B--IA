#!/bin/bash

# Script de démarrage pour ORLYNE-A12B

echo "╔════════════════════════════════════╗"
echo "║     ORLYNE-A12B - Démarrage        ║"
echo "╚════════════════════════════════════╝"

# Vérification de l'environnement
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activation de l'environnement virtuel
source venv/bin/activate

# Vérification des dépendances
echo "📦 Vérification des dépendances..."
pip install -r requirements.txt > /dev/null 2>&1

# Vérification de Docker
if command -v docker &> /dev/null; then
    echo "🐳 Docker détecté"
else
    echo "⚠️ Docker non installé (recommandé pour l'exécution de code)"
fi

# Vérification des dossiers nécessaires
mkdir -p data/models data/logs data/conversations

# Vérification du modèle
if [ ! -d "data/models/llama-3-8b" ]; then
    echo "📥 Téléchargement du modèle Llama 3 8B (premier lancement)..."
    python scripts/download_model.py
fi

# Démarrage
echo "🚀 Démarrage d'ORLYNE-A12B..."
echo "📡 Interface web: http://localhost:8000"
echo "📡 API: http://localhost:8000/docs"
echo ""

# Lancement
python -m src.main

# Nettoyage à l'arrêt
deactivate