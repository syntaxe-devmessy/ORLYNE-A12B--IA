# Dockerfile pour ORLYNE-A12B
# Image multi-stage pour optimisation

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Installation des dépendances de build
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .
COPY package.json .

# Installation des dépendances Python
RUN pip install --user --no-cache-dir -r requirements.txt

# Installation des dépendances Node (si nécessaire)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install --omit=dev \
    && apt-get remove -y nodejs \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Runtime
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

LABEL maintainer="Syntaxe Tech"
LABEL version="1.0.0"
LABEL description="ORLYNE-A12B - IA Assistant sans limites basée sur Llama 3 8B"

# Éviter les prompts interactifs
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    vim \
    htop \
    build-essential \
    libssl-dev \
    libffi-dev \
    libncurses5-dev \
    libsqlite3-dev \
    libreadline-dev \
    libbz2-dev \
    libgdbm-dev \
    zlib1g-dev \
    uuid-dev \
    lzma-dev \
    libopenblas-dev \
    liblzma-dev \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Installation de Docker pour l'exécution de code dans des conteneurs
RUN curl -fsSL https://get.docker.com -o get-docker.sh \
    && sh get-docker.sh \
    && rm get-docker.sh

# Création de l'utilisateur non-root
RUN useradd -m -u 1000 -s /bin/bash orlyne \
    && usermod -aG docker orlyne

# Création des dossiers nécessaires
RUN mkdir -p /app /data /models /data/logs /data/conversations /data/knowledge \
    && chown -R orlyne:orlyne /app /data /models

# Copie des dépendances Python depuis le builder
COPY --from=builder /root/.local /home/orlyne/.local
COPY --from=builder /node_modules /app/node_modules

# Copie du code source
COPY --chown=orlyne:orlyne . /app/

# Installation des dépendances Python restantes
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Création du lien symbolique pour python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Configuration du PATH
ENV PATH="/home/orlyne/.local/bin:${PATH}"
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Exposition des ports
EXPOSE 8000 8001 8765

# Volume pour les données persistantes
VOLUME ["/data", "/models", "/app/data"]

# Passage à l'utilisateur non-root
USER orlyne
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande par défaut
CMD ["python", "-m", "src.main"]