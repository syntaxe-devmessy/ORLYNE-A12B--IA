#!/bin/bash

# Script de sauvegarde pour ORLYNE-A12B

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="orlyne_backup_${TIMESTAMP}.tar.gz"

echo "💾 Sauvegarde d'ORLYNE-A12B..."

# Création du dossier de backup
mkdir -p $BACKUP_DIR

# Sauvegarde des données
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}" \
    data/ \
    .env \
    orlyne.json \
    2>/dev/null

# Sauvegarde des logs
tar -czf "${BACKUP_DIR}/logs_${TIMESTAMP}.tar.gz" \
    data/logs/ \
    2>/dev/null

echo "✅ Sauvegarde terminée: ${BACKUP_DIR}/${BACKUP_NAME}"
echo "📊 Taille: $(du -h ${BACKUP_DIR}/${BACKUP_NAME} | cut -f1)"

# Nettoyage des vieilles sauvegardes (plus de 30 jours)
find $BACKUP_DIR -name "orlyne_backup_*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "logs_*.tar.gz" -mtime +7 -delete