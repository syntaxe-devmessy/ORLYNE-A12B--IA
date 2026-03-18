#!/bin/bash

# Script d'entraînement pour ORLYNE-A12B

echo "🧠 Entraînement d'ORLYNE-A12B..."

# Activation de l'environnement
source venv/bin/activate

# Vérification des données d'entraînement
if [ ! -f "data/training/dataset.json" ]; then
    echo "📥 Téléchargement du dataset d'entraînement..."
    python scripts/download_dataset.py
fi

# Lancement de l'entraînement
echo "🚀 Démarrage de l'entraînement..."
python -m src.learning.trainer \
    --dataset data/training/dataset.json \
    --epochs 3 \
    --batch-size 4 \
    --learning-rate 1e-4 \
    --output-dir data/models/fine_tuned

echo "✅ Entraînement terminé"