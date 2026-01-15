#!/bin/bash

# Script de démarrage pour le frontend Next.js modernisé
# Remplace le script start-website.sh existant

echo "🚀 Démarrage du frontend Next.js modernisé..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"

# Load root .env so Next.js gets the variables even when launched from this script
if [ -f "$ROOT_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ROOT_DIR/.env"
    set +a
else
    echo "⚠️  Aucun fichier .env trouvé à la racine ($ROOT_DIR/.env)"
fi

# Navigate to the frontend directory
cd "$ROOT_DIR/apps/delphes/frontend" || exit 1

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

# Start the development server
echo "🌐 Démarrage du serveur de développement sur http://localhost:3000"
npm run dev
