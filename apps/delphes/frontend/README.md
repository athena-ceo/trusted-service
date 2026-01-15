# Site Web Officiel - Services de l'État dans les Yvelines

Site web moderne des services préfectoraux des Yvelines, développé avec Next.js 15 et entièrement conforme au Design System de l'État Français (DSFR). Interface gouvernementale officielle pour l'accueil des étrangers et les démarches administratives.

## 🚀 Démarrage rapide

### Prérequis
- Node.js 18+
- npm ou yarn

### Installation et lancement
```bash
# Installation des dépendances
npm install

# Développement
npm run dev
# Accès : http://localhost:3000

# Production
npm run build
npm start
```

## 🏗️ Architecture

### Structure des fichiers
```
src/
├── app/
│   ├── page.tsx                    # Page d'accueil officielle
│   ├── confirmation/page.tsx       # Page de confirmation des demandes
│   ├── accueil-etrangers/page.tsx  # Formulaire de contact avec IA
│   ├── layout.tsx                  # Layout principal avec DSFR
│   └── globals.css                 # Styles globaux
└── components/
    ├── ContactForm.tsx             # Formulaire de contact intelligent
    ├── Header.tsx                  # En-tête gouvernemental conforme
    └── Footer.tsx                  # Pied de page officiel
```

### Technologies utilisées
- **Next.js 15** : Framework React avec App Router et Turbopack
- **TypeScript** : Typage statique pour robustesse et maintenabilité
- **DSFR 1.12** : Design System officiel de l'État français
- **React 18** : Interface utilisateur moderne et performante

## ✨ Fonctionnalités principales

### Page d'accueil gouvernementale
- ✅ **Header DSFR complet** : Logo Marianne, navigation 5 menus, recherche
- ✅ **Navigation officielle** : Actualités, Actions de l'État, Services, Publications, Démarches
- ✅ **Section actualités authentique** : Images réelles du site yvelines.gouv.fr
- ✅ **Tuiles de démarches** : Carte grise, permis, CNI, passeport, accueil étrangers
- ✅ **Sidebar services** : Accueil étrangers, horaires, FAQ
- ✅ **Design responsive** : Mobile-first avec breakpoints DSFR

### Système de contact intelligent
- ✅ **Formulaire DSFR** : Validation temps réel avec messages d'erreur officiels
- ✅ **Analyse IA du message** : Classification automatique des demandes
- ✅ **Champs obligatoires** : Nom, prénom, email, arrondissement, message
- ✅ **Champ AGDREF** : Validation format (10 chiffres)
- ✅ **Conformité RGPD** : Acceptation obligatoire
- ✅ **API backend** : Intégration avec système d'analyse Python

## 🔧 Configuration et développement

### Variables d'environnement
Créer un fichier `.env.local` :
```
BACKEND_INTERNAL_URL=http://localhost:8002
NODE_ENV=development
```

### Scripts disponibles
```bash
npm run dev          # Serveur de développement (http://localhost:3000)
npm run build        # Build de production
npm run start        # Serveur de production
npm run lint         # Vérification ESLint
npm run type-check   # Vérification TypeScript
```

### Standards de développement
- **Composants TypeScript** : Props typés avec interfaces strictes
- **Styles DSFR uniquement** : Pas de CSS custom, utilisation exclusive du Design System
- **Structure gouvernementale** : Respect des guidelines officielles
- **Accessibilité RGAA** : Conformité niveau AA obligatoire
- **Hydratation SSR** : Attributs DSFR optimisés pour éviter les conflits client/serveur

## 🎨 Design System DSFR

### Composants utilisés
- `fr-header` : En-tête avec logo Marianne et navigation
- `fr-search-bar` : Barre de recherche gouvernementale
- `fr-nav` : Navigation principale 5 menus
- `fr-card` : Cartes actualités et démarches
- `fr-input` : Champs de formulaire avec validation
- `fr-alert` : Messages d'erreur et confirmation
- `fr-footer` : Pied de page gouvernemental

### Thème officiel
- **Couleurs** : Palette gouvernementale (bleu Marianne, rouge, gris)
- **Typographie** : Marianne (font officielle de l'État)
- **Icônes** : Remixicon + icônes DSFR officielles
- **Espacements** : Grille 8px conforme aux standards

## 🌐 Intégration backend

### API Python
Interface avec le backend d'analyse via :
- **URL** : `http://localhost:8002`
- **Endpoint principal** : `/analyze_with_response`
- **Format** : JSON avec analyse IA des demandes

### Flux de données
1. **Saisie utilisateur** : Formulaire DSFR avec validation
2. **Envoi sécurisé** : POST vers API d'analyse
3. **Traitement IA** : Classification automatique des demandes
4. **Retour utilisateur** : Page de confirmation avec référence

## 📱 Responsive et accessibilité

### Breakpoints DSFR
- **Mobile** : < 768px (navigation hamburger)
- **Tablette** : 768px - 992px (adaptation cards)
- **Desktop** : > 992px (layout complet)

### Accessibilité (RGAA)
- ✅ **Navigation clavier** : Tous les éléments focusables
- ✅ **Screen readers** : Labels et descriptions appropriés
- ✅ **Contraste** : Respect des ratios WCAG AA
- ✅ **Focus visible** : Indicateurs visuels clairs

## 🚀 Déploiement

### Build de production
```bash
npm run build       # Génération des assets optimisés
npm run start      # Serveur de production sur port 3000
```

### Optimisations incluses
- **Images** : Optimisation automatique Next.js
- **CSS** : Purge automatique des styles inutilisés
- **JavaScript** : Minification et tree-shaking
- **Cache** : Headers de cache optimaux pour assets statiques

## 📧 Support et maintenance

### Architecture modulaire
- Composants réutilisables et maintenables
- Séparation claire des responsabilités
- Configuration centralisée via environment

### Évolutions possibles
- Ajout de nouvelles pages de démarches
- Extension du système d'analyse IA
- Intégration avec d'autres APIs gouvernementales
- Dashboard administrateur pour le suivi des demandes

---
**Développé pour la Préfecture des Yvelines** - Conforme aux standards numériques de l'État français

### Intégration API
```typescript
// Analyse du message avec IA
POST /api/v1/analyze

// Traitement de la demande  
POST /api/v1/process_request

// Chargement des arrondissements
GET /api/v1/search_arrondissements
```

### Design responsif DSFR
- **Mobile-first** avec breakpoints officiels
- **Grille responsive** : formulaire principal (8/12) + sidebar info (4/12)
- **Accessibilité RGAA** conforme aux standards gouvernementaux
- **Navigation** avec breadcrumb et structure sémantique

## 🔧 Développement

### Scripts disponibles
```bash
npm run dev          # Serveur de développement
npm run build        # Build de production
npm run start        # Serveur de production
npm run lint         # Vérification ESLint
npm run type-check   # Vérification TypeScript
```

### Configuration

#### Proxy API
Le fichier `src/app/api/[...path]/route.ts` redirige automatiquement les appels vers l'API Python :
```
http://localhost:3000/api/v1/* → http://localhost:8002/api/v1/*
```

#### Variables d'environnement
```env
# .env.local (optionnel)
BACKEND_INTERNAL_URL=http://localhost:8002
```

## 🧪 Tests

### Test du formulaire
1. Aller sur http://localhost:3000
2. Cliquer sur "Préremplir le formulaire"
3. Vérifier la validation des champs
4. Tester la soumission avec l'API backend

### Validation des erreurs
- Champs vides → Messages d'erreur DSFR
- Email invalide → Validation format
- AGDREF → 10 chiffres exactement
- RGPD → Case obligatoire

## 📦 Production

### Build Docker
```bash
docker build -t delphes-frontend -f Dockerfile.delphes-frontend .
docker run -p 3000:3000 delphes-frontend
```

### Déploiement
L'application est optimisée pour :
- **Static export** (si pas d'API routes)
- **Server-side rendering** avec API routes
- **Docker containers**
- **Reverse proxy** (Nginx, Apache)

## 🔄 Migration depuis l'ancien site

### Avantages du nouveau frontend
- **Maintenabilité** : Code modulaire TypeScript vs HTML mélangé (1680 lignes → composants de ~150 lignes chacun)
- **Performance** : Rendu optimisé Next.js vs pages statiques lourdes
- **UX** : Validation temps réel vs validation côté serveur uniquement
- **Évolutivité** : Composants réutilisables vs code dupliqué
- **Tests** : Structure testable vs difficilement testable

### Compatibilité
- ✅ **API backend** : Aucun changement nécessaire
- ✅ **Fonctionnalités** : Toutes conservées et améliorées
- ✅ **Design** : Conformité DSFR maintenue
- ✅ **Accessibilité** : Standards RGAA respectés

## 📋 Roadmap

### Prochaines améliorations suggérées
1. **Tests unitaires** avec Jest/React Testing Library
2. **Tests e2e** avec Playwright
3. **Monitoring** avec analytics
4. **PWA** pour utilisation mobile offline
5. **Optimisations** performance (images, fonts)

### Extensibilité
- Architecture modulaire pour ajouter de nouvelles pages
- Composants réutilisables pour d'autres applications
- Configuration centralisée pour multi-tenant

---

## 📞 Support

Pour toute question sur ce frontend :
1. Consulter les logs de développement (`npm run dev`)
2. Vérifier la connectivité API backend
3. Tester avec les exemples de préremplissage

**Backend API requis** : `localhost:8002` avec endpoints `/api/v1/*`
