#!/bin/sh

# Script pour remplacer les variables d'environnement au runtime
# dans les fichiers JavaScript compilés de Next.js

echo "🔄 Substitution des variables d'environnement au runtime..."

# Afficher les variables pour debug
echo "📋 Variables à substituer:"
echo "   NEXT_PUBLIC_WATSON_REGION: ${NEXT_PUBLIC_WATSON_REGION:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_INSTANCE_ID: ${NEXT_PUBLIC_WATSON_INSTANCE_ID:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_INTEGRATION_ID: ${NEXT_PUBLIC_WATSON_INTEGRATION_ID:-'(non définie)'}"
echo "   NEXT_PUBLIC_WATSON_AGENT_ID: ${NEXT_PUBLIC_WATSON_AGENT_ID:-'(non définie)'}"

# Fonction pour remplacer les variables dans les fichiers
escape_sed() {
  printf '%s' "$1" | sed -e 's/[\/&|]/\\&/g'
}

substitute_vars() {
  local file="$1"

  cp "$file" "$file.backup" || return 1

  REGION_ESCAPED=$(escape_sed "${NEXT_PUBLIC_WATSON_REGION:-}")
  INSTANCE_ESCAPED=$(escape_sed "${NEXT_PUBLIC_WATSON_INSTANCE_ID:-}")
  INTEGRATION_ESCAPED=$(escape_sed "${NEXT_PUBLIC_WATSON_INTEGRATION_ID:-}")
  AGENT_ESCAPED=$(escape_sed "${NEXT_PUBLIC_WATSON_AGENT_ID:-}")

  sed -i \
    -e "s|__NEXT_PUBLIC_WATSON_REGION__|$REGION_ESCAPED|g" \
    -e "s|__NEXT_PUBLIC_WATSON_INSTANCE_ID__|$INSTANCE_ESCAPED|g" \
    -e "s|__NEXT_PUBLIC_WATSON_INTEGRATION_ID__|$INTEGRATION_ESCAPED|g" \
    -e "s|__NEXT_PUBLIC_WATSON_AGENT_ID__|$AGENT_ESCAPED|g" \
    "$file" \
  && rm -f "$file.backup" \
  || { mv "$file.backup" "$file"; return 1; }
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

echo "🔒 Verrouillage final du système de fichiers..."
su -c "chmod -R 555 /app" root 2>/dev/null || true

# Démarrer le serveur Next.js
echo "🚀 Démarrage du serveur Next.js..."
exec node server.js