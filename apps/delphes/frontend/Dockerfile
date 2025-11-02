# Dockerfile pour le frontend Next.js modernisé
# Supporte: linux/amd64, linux/arm64
FROM node:20-alpine AS base

# Installer les dépendances seulement quand nécessaire
FROM base AS deps
# Vérifier https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine pour comprendre pourquoi libc6-compat pourrait être nécessaire.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Installer les dépendances basées sur le gestionnaire de paquets préféré
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild le code source seulement quand nécessaire
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

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# server.js est créé par next build à partir du répertoire de sortie autonome
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output
CMD ["./substitute-env.sh"]
