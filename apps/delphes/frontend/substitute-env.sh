#!/bin/sh

# Script pour remplacer les variables d'environnement au runtime
# dans les fichiers JavaScript compilés de Next.js

echo "🔄 Substitution des variables d'environnement au runtime..."

# Fonction pour remplacer les variables dans les fichiers
substitute_vars() {
    local file="$1"
    local temp_file=$(mktemp)
    
    # Remplacer les placeholders par les vraies valeurs d'environnement
    sed \
        -e "s|__NEXT_PUBLIC_API_URL__|${NEXT_PUBLIC_API_URL:-}|g" \
        -e "s|__NEXT_PUBLIC_WATSON_REGION__|${NEXT_PUBLIC_WATSON_REGION:-}|g" \
        -e "s|__NEXT_PUBLIC_WATSON_INSTANCE_ID__|${NEXT_PUBLIC_WATSON_INSTANCE_ID:-}|g" \
        -e "s|__NEXT_PUBLIC_WATSON_INTEGRATION_ID__|${NEXT_PUBLIC_WATSON_INTEGRATION_ID:-}|g" \
        -e "s|__NEXT_PUBLIC_WATSON_AGENT_ID__|${NEXT_PUBLIC_WATSON_AGENT_ID:-}|g" \
        "$file" > "$temp_file" && mv "$temp_file" "$file"
}

# Chercher tous les fichiers JS dans le build Next.js
echo "📁 Recherche des fichiers à traiter..."
find /app/.next -name "*.js" -type f | while read -r file; do
    if grep -q "__NEXT_PUBLIC_" "$file" 2>/dev/null; then
        echo "🔧 Traitement: $file"
        substitute_vars "$file"
    fi
done

# Chercher dans les fichiers statiques aussi
find /app/.next/static -name "*.js" -type f 2>/dev/null | while read -r file; do
    if grep -q "__NEXT_PUBLIC_" "$file" 2>/dev/null; then
        echo "🔧 Traitement: $file"
        substitute_vars "$file"
    fi
done

echo "✅ Variables d'environnement substituées!"
echo "🚀 Démarrage du serveur Next.js..."

# Afficher les variables pour debug
echo "📋 Variables configurées:"
echo "   NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_REGION: ${NEXT_PUBLIC_WATSON_REGION:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_INSTANCE_ID: ${NEXT_PUBLIC_WATSON_INSTANCE_ID:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_INTEGRATION_ID: ${NEXT_PUBLIC_WATSON_INTEGRATION_ID:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_AGENT_ID: ${NEXT_PUBLIC_WATSON_AGENT_ID:-'(non définie)'}"

# Démarrer le serveur Next.js
exec node server.js