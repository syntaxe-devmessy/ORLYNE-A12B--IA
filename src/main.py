#!/usr/bin/env python3
"""
ORLYNE-A12B - IA Assistant avec Llama 3 8B
Développé par Syntaxe Tech
"""

import os
import sys
import logging
from pathlib import Path

# Ajout du chemin parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.engine import OrlyneEngine
from src.api.routes import create_app
from src.utils.logger import setup_logger

def main():
    """Point d'entrée principal d'Orlyne"""
    
    # Configuration du logging
    logger = setup_logger("orlyne")
    
    try:
        logger.info("🚀 Démarrage d'ORLYNE-A12B...")
        
        # Initialisation du moteur
        engine = OrlyneEngine()
        
        # Création de l'application web
        app = create_app(engine)
        
        # Démarrage du serveur
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()