#!/bin/bash

# Script d'installation pour ORLYNE-A12B
echo "🚀 Installation d'ORLYNE-A12B..."

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérification de pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 n'est pas installé"
    exit 1
fi

# Vérification de Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker n'est pas installé (recommandé pour l'exécution de code)"
fi

# Création de l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
echo "📦 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Création des dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p data/models data/knowledge data/conversations data/logs

# Téléchargement du modèle (optionnel)
echo "📥 Veux-tu télécharger le modèle Llama 3 maintenant ? (o/n)"
read -r download_model
if [ "$download_model" = "o" ]; then
    echo "📥 Téléchargement du modèle (peut prendre du temps)..."
    python scripts/download_model.py
fi

# Configuration
echo "⚙️ Création du fichier .env..."
cat > .env << EOF
# Configuration ORLYNE-A12B
ORLYNE_MODEL=meta-llama/Llama-3-8B
ORLYNE_DEVICE=cuda
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=INFO
EOF

echo "✅ Installation terminée !"
echo "Pour démarrer: ./scripts/start.sh"