#!/bin/sh

# Script pour remplacer les variables d'environnement au runtime
# dans les fichiers JavaScript compilés de Next.js

echo "🔄 Substitution des variables d'environnement au runtime..."

# Afficher les variables pour debug
echo "📋 Variables à substituer:"
echo "   NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_REGION: ${NEXT_PUBLIC_WATSON_REGION:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_INSTANCE_ID: ${NEXT_PUBLIC_WATSON_INSTANCE_ID:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_INTEGRATION_ID: ${NEXT_PUBLIC_WATSON_INTEGRATION_ID:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_AGENT_ID: ${NEXT_PUBLIC_WATSON_AGENT_ID:-'(non définie)'}"

# Fonction pour remplacer les variables dans les fichiers
substitute_vars() {
    local file="$1"
    
    # Créer une sauvegarde temporaire
    cp "$file" "$file.backup"
    
    # Remplacer les placeholders par les vraies valeurs d'environnement
    sed -i \
        -e "s|__NEXT_PUBLIC_API_URL__|${NEXT_PUBLIC_API_URL:-}|g" \
        -e "s|__NEXT_PUBLIC_WATSON_REGION__|${NEXT_PUBLIC_WATSON_REGION:-}|g" \
        -e "s|__NEXT_PUBLIC_WATSON_INSTANCE_ID__|${NEXT_PUBLIC_WATSON_INSTANCE_ID:-}|g" \
        -e "s|__NEXT_PUBLIC_WATSON_INTEGRATION_ID__|${NEXT_PUBLIC_WATSON_INTEGRATION_ID:-}|g" \
        -e "s|__NEXT_PUBLIC_WATSON_AGENT_ID__|${NEXT_PUBLIC_WATSON_AGENT_ID:-}|g" \
        "$file"
    
    # Vérifier si le remplacement a fonctionné
    if [ $? -eq 0 ]; then
        rm "$file.backup"
        return 0
    else
        # Restaurer en cas d'erreur
        mv "$file.backup" "$file"
        echo "❌ Erreur lors du remplacement dans $file"
        return 1
    fi
}

# Compter les fichiers traités
files_processed=0

# Chercher tous les fichiers JS dans le build Next.js
echo "📁 Recherche des fichiers à traiter..."
find /app/.next -name "*.js" -type f | while read -r file; do
    if grep -q "__NEXT_PUBLIC_" "$file" 2>/dev/null; then
        echo "🔧 Traitement: $file"
        substitute_vars "$file"
        if [ $? -eq 0 ]; then
            files_processed=$((files_processed + 1))
        fi
    fi
done

# Chercher dans les fichiers statiques aussi
find /app/.next/static -name "*.js" -type f 2>/dev/null | while read -r file; do
    if grep -q "__NEXT_PUBLIC_" "$file" 2>/dev/null; then
        echo "🔧 Traitement: $file"
        substitute_vars "$file"
        if [ $? -eq 0 ]; then
            files_processed=$((files_processed + 1))
        fi
    fi
done

echo "✅ Variables d'environnement substituées!"
echo "🚀 Démarrage du serveur Next.js..."

# Démarrer le serveur Next.js
exec node server.js