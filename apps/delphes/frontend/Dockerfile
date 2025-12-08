# Dockerfile pour le frontend Next.js modernisé
# Supporte: linux/amd64, linux/arm64
# ========== BASE ==========
FROM node:20-alpine AS base
WORKDIR /app

# Installer les dépendances basées sur le gestionnaire de paquets préféré
# ========== DEPS ==========
FROM base AS deps
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild le code source seulement quand nécessaire
# ========== BUILD ==========
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collecte des données de télémétrie complètement anonymes sur l'utilisation générale.
# En savoir plus ici: https://nextjs.org/telemetry
# Décommenter la ligne suivante au cas où vous voulez désactiver la télémétrie pendant le build.
ENV NEXT_TELEMETRY_DISABLED=1

# Forcer les placeholders pour la substitution runtime
ENV NEXT_PUBLIC_API_URL=__NEXT_PUBLIC_API_URL__
ENV NEXT_PUBLIC_WATSON_REGION=__NEXT_PUBLIC_WATSON_REGION__
ENV NEXT_PUBLIC_WATSON_INSTANCE_ID=__NEXT_PUBLIC_WATSON_INSTANCE_ID__
ENV NEXT_PUBLIC_WATSON_INTEGRATION_ID=__NEXT_PUBLIC_WATSON_INTEGRATION_ID__
ENV NEXT_PUBLIC_WATSON_AGENT_ID=__NEXT_PUBLIC_WATSON_AGENT_ID__

RUN npm run build

# Image de production, copier tous les fichiers et exécuter next
# ========== RUNNER ==========
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
# Décommenter la ligne suivante au cas où vous voulez désactiver la télémétrie pendant l'exécution.
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Définir automatiquement les permissions de sortie par défaut pour préserver la sécurité
# Copier manuellement les fichiers générés
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copier le script de substitution des variables d'environnement
COPY --chown=nextjs:nodejs substitute-env.sh ./
RUN chmod +x substitute-env.sh

USER root
RUN apk del busybox-extras || true

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://127.0.0.1:3000', r => process.exit(r.statusCode===200?0:1)).on('error', () => process.exit(1))"

# server.js est créé par next build à partir du répertoire de sortie autonome
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output
CMD ["./substitute-env.sh"]
