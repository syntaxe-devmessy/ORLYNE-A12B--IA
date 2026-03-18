# Makefile pour ORLYNE-A12B

.PHONY: help install start stop restart clean test lint format docker-build docker-run backup restore

# Couleurs
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help:
	@echo "$(BLUE)╔════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║     ORLYNE-A12B Makefile          ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "  $(YELLOW)make install$(NC)     - Installer les dépendances"
	@echo "  $(YELLOW)make start$(NC)       - Démarrer Orlyne"
	@echo "  $(YELLOW)make stop$(NC)        - Arrêter Orlyne"
	@echo "  $(YELLOW)make restart$(NC)     - Redémarrer Orlyne"
	@echo "  $(YELLOW)make clean$(NC)       - Nettoyer les fichiers temporaires"
	@echo "  $(YELLOW)make test$(NC)        - Lancer les tests"
	@echo "  $(YELLOW)make lint$(NC)        - Linter le code"
	@echo "  $(YELLOW)make format$(NC)      - Formater le code"
	@echo "  $(YELLOW)make docker-build$(NC)- Construire l'image Docker"
	@echo "  $(YELLOW)make docker-run$(NC)  - Lancer avec Docker"
	@echo "  $(YELLOW)make backup$(NC)      - Sauvegarder les données"
	@echo "  $(YELLOW)make restore$(NC)     - Restaurer les données"

install:
	@echo "$(GREEN)📦 Installation des dépendances...$(NC)"
	pip install -r requirements.txt
	npm install
	@echo "$(GREEN)✅ Installation terminée$(NC)"

start:
	@echo "$(GREEN)🚀 Démarrage d'ORLYNE...$(NC)"
	python -m src.main

stop:
	@echo "$(RED)🛑 Arrêt d'ORLYNE...$(NC)"
	pkill -f "python -m src.main" || true

restart: stop start

clean:
	@echo "$(YELLOW)🧹 Nettoyage...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

test:
	@echo "$(GREEN)🧪 Lancement des tests...$(NC)"
	pytest tests/ -v --cov=src --cov-report=html

lint:
	@echo "$(GREEN)🔍 Linting du code...$(NC)"
	flake8 src/
	pylint src/

format:
	@echo "$(GREEN)✨ Formatage du code...$(NC)"
	black src/
	isort src/

docker-build:
	@echo "$(GREEN)🐳 Construction de l'image Docker...$(NC)"
	docker-compose build

docker-run:
	@echo "$(GREEN)🐳 Lancement avec Docker...$(NC)"
	docker-compose up -d

docker-stop:
	@echo "$(RED)🐳 Arrêt des conteneurs...$(NC)"
	docker-compose down

docker-logs:
	docker-compose logs -f

backup:
	@echo "$(GREEN)💾 Sauvegarde des données...$(NC)"
	@mkdir -p backups
	@tar -czf backups/orlyne_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz data/
	@echo "$(GREEN)✅ Sauvegarde terminée dans backups/$(NC)"

restore:
	@echo "$(YELLOW)📂 Liste des sauvegardes disponibles:$(NC)"
	@ls -la backups/
	@read -p "Nom du fichier de backup: " filename; \
	if [ -f "backups/$$filename" ]; then \
		echo "$(GREEN)🔄 Restauration...$(NC)"; \
		tar -xzf "backups/$$filename"; \
		echo "$(GREEN)✅ Restauration terminée$(NC)"; \
	else \
		echo "$(RED)❌ Fichier non trouvé$(NC)"; \
	fi

monitor:
	@echo "$(GREEN)📊 Monitoring Orlyne...$(NC)"
	@watch -n 2 "curl -s http://localhost:8000/health | jq ."

logs:
	@tail -f data/logs/orlyne.log

shell:
	@python -m src.cli shell

train:
	@python -m scripts.train

update:
	@git pull
	@make install
	@make restart

.PHONY: help install start stop restart clean test lint format docker-build docker-run backup restore monitor logs shell train update