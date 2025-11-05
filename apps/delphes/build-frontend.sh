#!/bin/bash

# Script de build et déploiement du frontend Delphes
# Usage: ./build-frontend.sh [version]

set -e  # Arrêter en cas d'erreur

# Configuration
DOCKER_ORG="athenadecisionsystems"
IMAGE_NAME="delphes-frontend"
DOCKERFILE_PATH="frontend/Dockerfile"
BUILD_CONTEXT="frontend/"
PLATFORM="linux/amd64"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Vérifier que Docker est disponible
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé ou pas disponible dans le PATH"
    exit 1
fi

# Déterminer la version/tag
if [ $# -eq 0 ]; then
    # Si pas de version fournie, utiliser timestamp
    VERSION="$(date +%Y%m%d-%H%M%S)"
    warning "Aucune version spécifiée, utilisation de: $VERSION"
else
    VERSION="$1"
fi

FULL_IMAGE_NAME="${DOCKER_ORG}/${IMAGE_NAME}:${VERSION}"
LATEST_IMAGE_NAME="${DOCKER_ORG}/${IMAGE_NAME}:latest"

log "🚀 Début du build frontend Delphes"
log "📦 Image: $FULL_IMAGE_NAME"
log "🏗️  Plateforme: $PLATFORM"

# Vérifier que les fichiers nécessaires existent
if [ ! -f "$DOCKERFILE_PATH" ]; then
    error "Dockerfile introuvable: $DOCKERFILE_PATH"
    exit 1
fi

if [ ! -d "$BUILD_CONTEXT" ]; then
    error "Contexte de build introuvable: $BUILD_CONTEXT"
    exit 1
fi

# Construire l'image Docker
log "🔨 Construction de l'image Docker..."
if docker buildx build \
    --platform "$PLATFORM" \
    -t "$FULL_IMAGE_NAME" \
    -t "$LATEST_IMAGE_NAME" \
    --push \
    -f "$DOCKERFILE_PATH" \
    "$BUILD_CONTEXT"; then
    success "✅ Image construite et poussée avec succès"
else
    error "❌ Échec de la construction de l'image"
    exit 1
fi

# Mettre à jour docker-compose.prod.yml
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    log "📝 Mise à jour de $DOCKER_COMPOSE_FILE..."
    
    # Sauvegarder le fichier original
    cp "$DOCKER_COMPOSE_FILE" "${DOCKER_COMPOSE_FILE}.backup"
    
    # Remplacer l'image dans docker-compose
    sed -i.tmp "s|image: ${DOCKER_ORG}/${IMAGE_NAME}:.*|image: ${FULL_IMAGE_NAME}|g" "$DOCKER_COMPOSE_FILE"
    rm "${DOCKER_COMPOSE_FILE}.tmp"
    
    success "✅ $DOCKER_COMPOSE_FILE mis à jour avec l'image $FULL_IMAGE_NAME"
else
    warning "⚠️  Fichier $DOCKER_COMPOSE_FILE introuvable"
fi

# Afficher les informations de déploiement
log "📋 Informations de déploiement:"
echo "   🏷️  Version: $VERSION"
echo "   📦 Image complète: $FULL_IMAGE_NAME"
echo "   🔗 Image latest: $LATEST_IMAGE_NAME"
echo ""
log "🚀 Commandes pour déployer sur le serveur:"
echo "   docker-compose -f docker-compose.prod.yml pull"
echo "   docker-compose -f docker-compose.prod.yml down"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🧹 Nettoyage des images Docker..."
echo "   docker image prune -f"
echo ""

success "🎉 Build terminé avec succès!"
echo ""
