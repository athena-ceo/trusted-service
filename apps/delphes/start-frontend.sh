#!/bin/bash

# Script de démarrage pour le frontend Next.js modernisé
# Remplace le script start-website.sh existant

echo "🚀 Démarrage du frontend Next.js modernisé..."

# Navigate to the frontend directory
cd "$(dirname "$0")/frontend" || exit 1

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

# Start the development server
echo "🌐 Démarrage du serveur de développement sur http://localhost:3000"
npm run dev
