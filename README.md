# Trusted Services - Plateforme IA pour Services Publics

[![Next.js](https://img.shields.io/badge/Next.js-15.5.4-black)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.1.0-blue)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-009688)](https://fastapi.tiangolo.com/)
[![DSFR](https://img.shields.io/badge/DSFR-1.14.2-blue)](https://www.systeme-de-design.gouv.fr/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://typescriptlang.org/)

> 🏛️ **Plateforme intelligente pour l'automatisation et l'amélioration des services publics français**

Une solution complète combinant intelligence artificielle et design system gouvernemental pour moderniser l'accueil et le traitement des demandes citoyennes.

## 🚀 Aperçu du Projet

**Trusted Services** est une plateforme innovante qui transforme l'expérience des services publics en intégrant :

- **🤖 IA conversationnelle** avec Watson Orchestrate pour l'assistance citoyenne
- **📋 Analyse automatique** des demandes avec détection d'intentions
- **🎨 Interface moderne** conforme DSFR (Design System de l'État)
- **⚡ Performance optimisée** avec Next.js 15 et React 19
- **♿ Accessibilité RGAA** respectant les standards gouvernementaux

### 🎯 Cas d'usage : Préfecture des Yvelines (Delphes)

Le projet pilote modernise l'accueil des étrangers en préfecture avec :
- Formulaire intelligent de prise de rendez-vous
- Traitement automatique des demandes complexes
- Interface responsive multilingue (FR/EN)
- Intégration complète avec les systèmes existants

---

## 📋 Table des Matières

- [🚀 Démarrage Rapide](#-démarrage-rapide)
- [🏗️ Architecture](#️-architecture)
- [💻 Frontend Next.js](#-frontend-nextjs)
- [🤖 Intégration IA](#-intégration-ia)
- [🛠️ Installation](#️-installation)
- [⚙️ Configuration](#️-configuration)
- [🔧 API et Backend](#-api-et-backend)
- [📦 Déploiement](#-déploiement)
- [🌐 Localisation](#-localisation)
- [🔍 Débogage](#-débogage)
- [📚 Documentation](#-documentation)

---

## 🚀 Démarrage Rapide

### Mode Développement Complet

```bash
# 1. Cloner et installer
git clone <repository-url>
cd trusted-service

# 2. Backend Python
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -r requirements.txt

# 3. Frontend Next.js
cd apps/delphes/frontend
npm install

# 4. Lancer en parallèle
# Terminal 1 - API Backend
python launcher_api.py ./runtime

# Terminal 2 - Frontend Next.js
cd apps/delphes/frontend
npm run dev
```

🌐 **Accès** :
- Frontend : http://localhost:3000
- API Backend : http://localhost:8002
- Documentation API : http://localhost:8002/docs

### Mode Demo Streamlit (Legacy)

```bash
# Demo intégrée (client + serveur)
streamlit run launcher_testclient.py ./runtime direct

# Ou mode API REST
python launcher_api.py ./runtime
streamlit run launcher_testclient.py ./runtime rest
```

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Next.js App] --> B[React Components]
        B --> C[DSFR Design System]
    end
    
    subgraph "API Layer"
        D[FastAPI Server] --> E[REST Endpoints]
        E --> F[Python Backend]
    end
    
    subgraph "AI Layer"
        G[Watson Orchestrate] --> H[LLM Analysis]
        H --> I[Intent Detection]
    end
    
    subgraph "Data Layer"
        J[Excel Config] --> K[Cache System]
        K --> L[Email Integration]
    end
    
    A --> D
    F --> G
    F --> J
```

### Structure du Projet

```
trusted-service/
├── 🎨 apps/delphes/frontend/     # Frontend Next.js moderne
│   ├── src/app/                  # Pages et composants React
│   ├── public/                   # Assets statiques
│   └── package.json              # Dépendances Node.js
├── 🔧 src/                       # Backend Python
│   ├── backend/                  # API FastAPI
│   ├── client/                   # Clients API
│   ├── common/                   # Utilitaires partagés
│   └── text_analysis/            # Moteur IA
├── 🗃️ runtime/                   # Configuration et données
│   ├── config_*.yaml            # Configurations serveur
│   ├── apps/                     # Apps métier (AISA, Delphes...)
│   └── cache/                    # Cache des analyses
└── 📋 requirements.txt           # Dépendances Python
```
---

## 💻 Frontend Next.js

### 🎨 Interface Moderne DSFR

Le frontend Next.js offre une expérience utilisateur moderne tout en respectant les standards gouvernementaux français.

#### 🔧 Technologies

- **Framework** : Next.js 15.5.4 avec Turbopack
- **UI Library** : React 19.1.0 avec TypeScript 5.0+
- **Design System** : DSFR 1.14.2 (@gouvfr/dsfr)
- **Composants** : @codegouvfr/react-dsfr 1.28.0
- **HTTP Client** : Axios 1.12.2 avec SWR 2.3.6
- **Styles** : TailwindCSS 4.0+ intégré

#### 🚀 Fonctionnalités Clés

- ✅ **Formulaire intelligent** avec validation temps réel
- ✅ **Analyse IA des demandes** avec détection d'intentions automatique
- ✅ **Champs conditionnels** qui s'adaptent selon le type de demande
- ✅ **Conversion de dates** française (JJ/MM/AAAA) ↔ ISO (AAAA-MM-JJ)
- ✅ **Interface responsive** optimisée mobile/desktop
- ✅ **Watson Orchestrate** intégré pour assistance IA
- ✅ **Accessibilité RGAA** conforme standards gouvernementaux
- ✅ **Gestion d'état** localStorage pour flux multi-pages
- ✅ **API Proxy** transparent vers backend Python

#### 📁 Structure Frontend

```
apps/delphes/frontend/src/
├── app/
│   ├── page.tsx                    # 🏠 Page d'accueil avec redirection
│   ├── accueil-etrangers/
│   │   └── page.tsx               # 📝 Formulaire de contact principal
│   ├── analysis/
│   │   └── page.tsx               # 🤖 Page d'analyse IA avec champs dynamiques
│   ├── handle-case/
│   │   └── page.tsx               # 💼 Traitement du dossier + Watson Orchestrate
│   ├── confirmation/
│   │   └── page.tsx               # ✅ Page de confirmation
│   ├── api/[...path]/
│   │   └── route.ts               # 🔗 Proxy API vers backend Python
│   ├── globals.css                # 🎨 Styles globaux DSFR
│   └── layout.tsx                 # 📐 Layout principal de l'application
├── components/
│   ├── ContactForm.tsx            # 📋 Composant formulaire réutilisable
│   ├── Header.tsx                 # 🎯 En-tête gouvernemental DSFR
│   ├── Footer.tsx                 # 📄 Pied de page avec liens utiles
│   └── Spinner.css               # ⏳ Animation de chargement
└── utils/
    ├── convertDateToISO.ts        # 🗓️ Conversion date FR → ISO
    └── convertISOToDate.ts        # 🗓️ Conversion date ISO → FR
```

#### 🔄 Flux de Données

```mermaid
sequenceDiagram
    participant User
    participant Form as ContactForm
    participant Analysis as Analysis Page
    participant API as Python Backend
    participant Watson as Watson Orchestrate
    participant HandleCase as Handle Case

    User->>Form: Remplit le formulaire
    Form->>Analysis: localStorage + navigation
    Analysis->>API: POST /analyze_request
    API-->>Analysis: intentions + champs requis
    User->>Analysis: Sélectionne intention + remplit champs
    Analysis->>HandleCase: localStorage + navigation
    HandleCase->>API: POST /handle_case
    HandleCase->>Watson: Charge assistant IA
    Watson-->>User: Assistance conversationnelle
```

---

## 🤖 Intégration IA

### Watson Orchestrate

Le chatbot Watson Orchestrate est intégré dans la page `handle-case` pour fournir une assistance IA contextuelle.

#### Configuration

```typescript
// Configuration Watson dans handle-case/page.tsx
const wxOConfiguration = {
    orchestrationID: "0781f29958be4f588e177e1250f85e99_b50c4815-0abc-4da6-a4e0-c6371abd1ebc",
    hostURL: "https://us-south.watson-orchestrate.cloud.ibm.com",
    rootElementID: "watson-chat-container", // ⚠️ Évite conflit avec React
    deploymentPlatform: "ibmcloud",
    chatOptions: {
        agentId: "51e5378a-e601-44c4-b2af-4f574177bd6e"
    }
};
```

#### Fonctionnalités IA

- **🎯 Détection d'intentions** : Classification automatique des demandes
- **📝 Champs dynamiques** : Génération de formulaires adaptatifs
- **🗓️ Parsing de dates** : Reconnaissance intelligente de formats temporels
- **✅ Validation contextuelle** : Vérification des données selon l'intention
- **💬 Assistance conversationnelle** : Support utilisateur en temps réel

### Backend Text Analysis

```python
# Moteur d'analyse dans src/text_analysis/
├── llm_ollama.py          # Interface Ollama locale
├── llm_openai.py          # Interface OpenAI/Azure
├── base_models.py         # Modèles de données
└── text_analysis_localization.py  # Support multilingue
```

---

## 🛠️ Installation

### Prérequis

- **Python** 3.11+ avec pip
- **Node.js** 18+ avec npm
- **Git** pour le versioning

### Installation Backend

```bash
# Environnement virtuel Python
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Dépendances Python
pip install -r requirements.txt

# Vérification
python -c "import fastapi, uvicorn; print('✅ Backend ready')"
```

### Installation Frontend

```bash
# Navigation vers frontend
cd apps/delphes/frontend

# Installation dépendances
npm install

# Vérification
npm run build
echo "✅ Frontend ready"
```

### Variables d'Environnement

Créer `.env.local` dans `apps/delphes/frontend/` :

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8002

# Watson Orchestrate (optionnel)
NEXT_PUBLIC_WATSON_ORCHESTRATION_ID=your_orchestration_id
NEXT_PUBLIC_WATSON_HOST_URL=https://us-south.watson-orchestrate.cloud.ibm.com

# Environment
NODE_ENV=development
```

---

## ⚙️ Configuration

### Configuration Runtime

Le système utilise des fichiers YAML pour la configuration :

```yaml
# runtime/config_server.yaml
server:
  host: "127.0.0.1"
  port: 8002
  reload: true

# runtime/config_connection.yaml
llm_providers:
  openai:
    api_key: "your_api_key"
    model: "gpt-4"
  ollama:
    base_url: "http://localhost:11434"
    model: "llama2"
```

### Configuration Applications

Chaque application a sa configuration Excel dans `runtime/apps/` :

```
runtime/apps/
├── delphes/
│   ├── delphes.xlsx        # Configuration métier
│   ├── data_enrichment.py  # Enrichissement données
│   └── decision_engine.py  # Moteur de décision
├── AISA/
│   └── AISA.xlsx          # Application AISA
└── conneXion/
    └── conneXion.xlsx     # Application ConneXion
```

### Structure Excel

Les fichiers Excel définissent :
- **Intentions** : Types de demandes supportées
- **Champs** : Données requises par intention
- **Localisations** : Traductions FR/EN
- **Workflows** : Processus de traitement
- **Emails** : Templates de notification

---

## 🔧 API et Backend

### Architecture FastAPI

```python
# src/backend/app.py - Point d'entrée principal
from fastapi import FastAPI
from src.backend.rest import router

app = FastAPI(
    title="Trusted Services API",
    description="API pour services publics intelligents",
    version="1.0.0"
)

app.include_router(router, prefix="/api")
```

### Endpoints Principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/analyze_request` | POST | Analyse IA d'une demande |
| `/api/handle_case` | POST | Traitement complet d'un dossier |
| `/api/get_intentions` | GET | Liste des intentions disponibles |
| `/api/health` | GET | Statut de l'API |
| `/docs` | GET | Documentation Swagger |

### Exemples d'utilisation

```bash
# Analyse d'une demande
curl -X POST "http://localhost:8002/api/analyze_request" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "delphes",
    "locale": "fr",
    "message": "Je souhaite renouveler mon titre de séjour"
  }'

# Traitement d'un dossier
curl -X POST "http://localhost:8002/api/handle_case" \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "delphes",
    "locale": "fr",
    "field_values": {
      "nom": "Dupont",
      "prenom": "Jean",
      "date_naissance": "1990-01-15"
    },
    "selected_intention": "renouvellement_titre_sejour"
  }'
```

---

## 📦 Déploiement

### Mode Production

```bash
# Build Frontend
cd apps/delphes/frontend
npm run build
npm run start  # Port 3000

# Backend Production
uvicorn src.backend.app:app \
  --host 0.0.0.0 \
  --port 8002 \
  --workers 4
```

### Docker (Recommandé)

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8002
CMD ["uvicorn", "src.backend.app:app", "--host", "0.0.0.0", "--port", "8002"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build:
      context: ./apps/delphes/frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://backend:8002
    depends_on:
      - backend

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8002:8002"
    volumes:
      - ./runtime:/app/runtime
    environment:
      - PYTHON_PATH=/app
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/trusted-services
server {
    listen 80;
    server_name your-domain.gouv.fr;

    # Frontend Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API Backend
    location /api/ {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Assets statiques
    location /static/ {
        alias /var/www/trusted-services/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 🌐 Localisation

### Support Multilingue

Le système supporte actuellement :
- 🇫🇷 **Français** (`fr`) - Langue principale
- 🇬🇧 **Anglais** (`en`) - Traduction complète

### Ajouter une Nouvelle Langue

Pour ajouter le support d'une nouvelle langue (ex: `es` pour l'espagnol) :

#### 1. Mise à jour du code Python

```python
# src/common/configuration.py
class SupportedLocale(str, Enum):
    fr = "fr"
    en = "en"
    es = "es"  # ← Ajouter ici

# src/backend/text_analysis/text_analysis_localization.py
# IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
# Add here support for new languages
SUPPORTED_LOCALES = ["fr", "en", "es"]  # ← Ajouter ici
```

#### 2. Configuration Excel

Dans `runtime/apps/delphes/delphes.xlsx` :
- Dupliquer les colonnes `*_fr` en `*_es`
- Traduire le contenu avec un LLM
- Conserver les noms officiels sans traduction

#### 3. Frontend Next.js

```typescript
// src/app/layout.tsx
const locales = ['fr', 'en', 'es'];  // ← Ajouter ici

// Créer les fichiers de traduction
// locales/es.json
{
  "contact_form": {
    "title": "Formulario de contacto",
    "submit": "Enviar"
  }
}
```

### Bonnes Pratiques

- ✅ Utiliser un LLM pour les traductions avec contexte métier
- ✅ Conserver les termes officiels (ex: "AES: admission exceptionnelle au séjour")
- ✅ Tester chaque langue sur tous les parcours utilisateur
- ✅ Éviter les underscores dans les codes langue

---

## 🔍 Débogage

### Logs et Monitoring

```bash
# Logs Backend détaillés
python launcher_api.py ./runtime --log-level debug

# Logs Frontend Next.js
cd apps/delphes/frontend
npm run dev  # Mode verbose automatique

# Logs Watson Orchestrate
# Vérifier la console navigateur pour les erreurs de script
```

### Problèmes Courants

#### 🚨 Erreur "Minified React error #321"

**Cause** : Conflit d'ID entre React et Watson Orchestrate

**Solution** : Vérifier que `rootElementID` dans Watson config utilise un ID unique (pas "root")

```typescript
// ❌ Incorrect
rootElementID: "root"  // Conflit avec React

// ✅ Correct  
rootElementID: "watson-chat-container"
```

#### 🚨 CORS Error sur API

**Cause** : Configuration CORS manquante

**Solution** : Vérifier la configuration FastAPI

```python
# src/backend/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 🚨 Champs de formulaire non remplis

**Cause** : Mismatch entre noms de champs backend/frontend

**Solution** : Vérifier la correspondance dans `ContactForm.tsx`

```typescript
// Mapping des noms de champs
const fieldMapping = {
  'date_naissance': 'dateNaissance',
  'situation_familiale': 'situationFamiliale',
  // etc...
};
```

#### 🚨 Watson Orchestrate ne se charge pas

**Causes possibles** :
- Script bloqué par politique CSP
- ID container introuvable
- Configuration incorrecte

**Diagnostic** :
```javascript
// Console navigateur
console.log(window.wxOConfiguration);
console.log(document.getElementById('watson-chat-container'));
```

### Outils de Debug

```bash
# Vérification de l'état des services
curl http://localhost:8002/api/health
curl http://localhost:3000/api/health

# Test des endpoints API
curl -X POST http://localhost:8002/api/analyze_request \
  -H "Content-Type: application/json" \
  -d '{"app_name":"delphes","locale":"fr","message":"test"}'

# Validation des configurations
python -c "
import yaml
with open('runtime/config_server.yaml') as f:
    print(yaml.safe_load(f))
"
```

---

## 📚 Documentation

### Ressources Supplémentaires

- **[Frontend README](apps/delphes/frontend/README.md)** - Documentation Next.js spécifique
- **[Delphes README](apps/delphes/README.md)** - Documentation application métier
- **[ODM README](src/backend/decision/decision_odm/README.md)** - Moteur de décision

### Standards et Références

- **[DSFR Documentation](https://www.systeme-de-design.gouv.fr/)** - Design System gouvernemental
- **[RGAA Guidelines](https://accessibilite.numerique.gouv.fr/)** - Accessibilité numérique
- **[Next.js Docs](https://nextjs.org/docs)** - Framework React
- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - API Python moderne

### APIs Externes

- **[Watson Orchestrate](https://www.ibm.com/cloud/watson-orchestrate)** - Plateforme IA IBM
- **[OpenAI API](https://platform.openai.com/docs)** - Modèles de langage
- **[Ollama](https://ollama.ai/)** - LLM local

---

## 👥 Contribution

### Workflow Git

```bash
# Créer une branche feature
git checkout -b feature/nouvelle-fonctionnalite

# Développement avec commits atomiques
git add .
git commit -m "feat: ajouter fonction X"

# Push et Pull Request
git push origin feature/nouvelle-fonctionnalite
# Créer PR sur GitHub
```

### Standards de Code

- **Python** : Black, isort, mypy
- **TypeScript** : ESLint, Prettier
- **Commits** : Convention [Conventional Commits](https://conventionalcommits.org/)

### Tests

```bash
# Tests Backend
python -m pytest src/tests/

# Tests Frontend  
cd apps/delphes/frontend
npm run test

# Tests E2E
npm run test:e2e
```

---

## 📄 Licence

Ce projet est sous licence propriétaire Athena. Tous droits réservés.

---

## 📞 Support

Pour toute question ou problème :

1. **Issues GitHub** : Créer un ticket détaillé
2. **Documentation** : Consulter les README spécifiques
3. **Logs** : Joindre les logs d'erreur complets
4. **Contact** : équipe-dev@athena.fr

---

*Dernière mise à jour : 3 octobre 2025*

#### Avantages vs ancien site statique
- **Maintenabilité** : Code modulaire TypeScript vs HTML mélangé
- **Performance** : Rendu optimisé Next.js vs pages statiques lourdes  
- **UX** : Validation temps réel vs validation côté serveur uniquement
- **Évolutivité** : Composants réutilisables vs code dupliqué
- **Tests** : Structure testable vs difficilement testable

Pour plus de détails, consultez le [README frontend](apps/delphes/frontend/README.md).

## What is Trusted Services?

Trusted Services is an application server and a LOW CODE development framework that streamline the build of localizable,
accountable, self-service applications.

Trusted Services app follow a well defined flow:

- The requester is filling-in basic information in a flow
- The requester is describing his situation and need in natural language
- A **LLM-based text analyzer** is determining the intent among a list of predefined ones, and is extracting structured
  information from the natural language message
- Ths user is confirming the intent and extracted data
- A **rule-based decision engine** is determining the case priority and where to route the case
- A **distribution component** (e-mail, ticketing, case management) is posting the case along with insight to help the
  agent process the case

Defining a new application requires defining the application model and the decision rules:

1. The application model defines the predefined intents and the fields (such as "name", "date of application") that
   structure a case. It can be defined through an API or by configuring an Excel document. This README.md focuses on
   Excel-based approach.
2. The rules implement the following decisions:

- The (localized) messages to showw to the requester
- The priority attached to a new case
- The basket where to route it
- The alerts that must be brpought to the agent attention
- A recommended response that the agent can amend

------
This README shows the second approach on an example: The Delphes project (Projet de la Préfecture des Yvelines) that

- streamlines the experience of foreigners requesting services related to their stay in France
- improves the efficiency of the back-office agents in charge of processing these requests
- makes the entire chain far more trustable than the legacy email-based approach.

Applications built with the framework implement an **accountable AI pattern** with 4 major components:

- The requester
- A LLM service
- A rule-based decision service
- The back-office agent

Both the requester and the agent are "humans in the loop", as they validate AI-generated findings.
------
More details can be found in the pptx in subdirectory `docs` of the current git repository. Also, to understand the
architecture and design of the Trusted Services framework, you should check the UML diagram in
`docs/trusted_services_uml.drawio`

## Git Repository Contents

This git repository comes with:

- The source code of the Trusted Services server
- A generic Streamlit test client  
- **🆕 Modern React/Next.js frontend** for Delphes (apps/delphes/frontend/)
- Two application definition Excel files: One for the Delphes app, and one for a self-service app for a fictitious telco
  operator.

### Frontend Architecture

- **Legacy**: Static HTML website (apps/delphes/runtime/website/)
- **Modern**: React/Next.js application (apps/delphes/frontend/) 
  - Production-ready with TypeScript
  - DSFR design system compliance
  - Modular component architecture
  - API integration with existing Python backend

## Installation

### Get the Trusted Service and the sample applications

Type

```
git clone https://github.com/athena-ceo/trusted-service.git
python3.12 -m venv .venv
. .venv/bin/activate (or source .venv/scripts/Activate)
pip install -r requirements.txt
```

### 🆕 Installation du frontend moderne (optionnel)

Pour utiliser la nouvelle interface React/Next.js pour Delphes :

```bash
cd apps/delphes/frontend
npm install

# Développement
npm run dev  # Frontend sur http://localhost:3000

# Production  
npm run build
npm start
```

**Prérequis** : Node.js 18+ et npm/yarn

### Download and install Docker Desktop and the Official IBM Operational Decision Manager for Developers image if you need to use the ODM Decision Engine

Please follow the instructions in https://hub.docker.com/r/ibmcom/odm

### Specifically for the Delphes application, download and install Thunderbird

Visit https://www.thunderbird.net/en-US/download/


## Athena Server Environment

### Connect to Athena Servers

``` 
ssh yourname@apps.athenadecisions.com
```
If you haven't changed your password, try `Athena4ever`.

Don't forget to set your env variables (OPENAI_API_KEY, SCW_PROJECT_ID, SCW_SECRET_KEY).

```
cd /data/demos/trusted-services
git pull
. .venv/bin/activate
```

### Launch the test client

```
streamlit run launcher_testclient.py ./runtime direct
```

The test client's url is `https://apps.athenadecisions.com/trusted-services-test-client/`. A shortcut is displayed on the home page: `https://apps.athenadecisions.com`.

If you would like to run Streamlit (or the server) and close your connection, use the following command:

```
nohup streamlit run launcher_testclient.py ./runtime direct > server.log 2>&1 &
```

If you would like to know if the test client (or server) is currently running:

```
ps -ef|grep streamlit
```
or
```
ps -ef|grep python
```
(Be carefull, we're running Python in a shared system. Another Athenian may be running another Python process at the moment.)

## Configuration

Trusted Services apps are configured in an Excel file. For Delphes check `apps\delphes\runtime\spec_delphes_ff.xlsx` (**TO BE UPDATED**)
where fields are either self-explanatory or explained in a comment cell.

### Configure how the test client accesses the API

- The Streamlist test client can either connect to the API through function calls or through REST calls
- To configure how the test client accesses the API, switch the Excel file to tab `frontend`. Field `connection_to_api`
  has two possible values
    - `direct`: Direct access through Python function
    - `rest`: REST calls to the Uvicorn server. In that case, you will need to launch the uvicorn server (see below) and
      to configure `rest_api_host` and `rest_api_port`

### Configure what Decision Engine the API connects to

- The API either connects to ODM, Drools or a hardcoded engine (in the case of Delphes:
  `apps.delphes.src.app_delphes.CaseHandlingDecisionEngineDelphesPython`)
- To configure hwhat Decision Engine the API connects to, switch the Excel file to tab `backend`. Field
  `decision_engine` has three possible values
    - `odm`: Connect to an ODM Decision Service. In that case, you will need to launch the ODM Docker image (see below)
      and to configure the `odm` tab
    - `drools`: Connect to a Drools Decision Service
    - `apps.delphes.design_time.src.app_delphes.CaseHandlingDecisionEngineDelphesPython`: Connect to a hardcoded
      Decision Service

## Run

Proceed in the following order:

### Option A: Frontend moderne Next.js (Recommandé pour Delphes)

1. **Lancer l'API backend Python**
   ```bash
   python launcher_api.py ./runtime
   # API disponible sur http://localhost:8002
   ```

2. **Lancer le frontend React/Next.js** 
   ```bash
   cd apps/delphes/frontend
   npm run dev
   # Frontend disponible sur http://localhost:3000
   ```

3. **Tester l'application**
   - Aller sur http://localhost:3000
   - Utiliser le bouton "Préremplir le formulaire" pour un test rapide
   - Vérifier que la soumission fonctionne avec l'API backend

### Option B: Interface traditionnelle Streamlit

Si vous préférez utiliser l'interface Streamlit existante :

### If you configured the Decision Engine to be ODM, launch the ODM Docker image

**Important notes**:
> **1. ODM Decision Center database persistence locale**
>
> A given instance of the ODM Decision Center database has a native locale and cannot host rules with a different
> persitence locale.
>
> To set the locale (en_US by default):
>> - launch the ODM Docker image
>> - remove all rules
>> - run `odm_dc_localization.py` in `src/backend/decision/decision_odm/admin`
>
> 3. ODM Version
     > The `-v` option in the docker command ensure the Decision Center and RES databases are backed by a file.
     > Nothing will ensure that the format of the files doesn't change. Therefore it is advised to have a directory per
     ODM version.

This leads to the following command for Delphes!

```
cd apps/delphes/runtime/odm_databases/9.0
docker run -e LICENSE=accept -m 2048M --memory-reservation 2048M -p 9060:9060 -p 9443:9443 -v .:/config/dbdata/ -e SAMPLE=false icr.io/cpopen/odm-k8s/odm:9.0
```

### Unless you only want to launch the test client, and you configured that client to access the API directly, launch the uvicorn server

In the `trusted-service` top directory, type:

```
python launcher_uvicorn.py ./apps/delphes/runtime/spec_delphes_ff.xlsx
```

### Launch the test client

In the `trusted-service` top directory, type:

```
streamlit run launcher_streamlit_direct.py apps/delphes/design_time/appdef_delphes_ff.xlsx apps/conneXion/design_time/appdef_conneXion_ff.xlsx

```

You should see a message such as:
> You can now view your Streamlit app in your browser.
> Local URL: http://localhost:8501

Click the link to launch the app in your default browser.

**Warning** If you need to run the Streamlit test client (or any other http client) on another port than 8501, update
cell `common > client_url` in the configuration xlsxx file.

## Common tasks

### Defining a Trusted Services app through Excel configuration

### Adding support for a new language in the Trusted Services framework

Each language supported is identified by a string, such as "fr_FR" (French of France) or "fr" (General French, in
practice identical to fr_FR). As of today, the supported languages are: `fr` and `en`.
If you need to add support for a new language, for instance `fi` (Finnish):

- Add `fi` to the list above
- Update the Trusted Services framework Python code. To do so, look for the following comment:
    ```
    # IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
    # Add here support for new languages
    ```
  in the following files:
    - `trusted-service/src/common/configuration.py` (definition of `SupportedLocale`)
    - `trusted-service/src/backend/text_analysis/text_analysis_localization.py`
    - `trusted-service/src/sample_frontend/frontend_localization.py`
    - `trusted-service/src/sample_frontend/streamlit_main.py`

### Localizing an existing application

- First, make sure there exists support for the language in the Trusted Services framework
- Second, follow the steps below, shown on what it took to localize the Delphes app to `en`, initially supporting `fr`
  only
  This is an illustration on Delphes, which was supporting `fr` initially. Below are the steps followed to support `en`
  too
- In `./apps/delphes/runtime/spec_delphes_ff.xlsx` duplicate all rows and columns labeled `<property>_fr` and label the
  duplicate row or column `<property>_en`
- Best practices:
    - Translate the content with a LLM and give a bit of context in the prompt
    - Do not translate official names such as "AES: admission exceptionnelle au séjour", but provide extra explanation
      in English

### Best practices for localizing an existing application

- Copy-paste the configuation from a language your application already support
- Use a LLM
- No _ in locale

## Troubleshooting

- If you are not receiving the emails as you would expect, check `send_email` in tab `email_configuration` of the Excel
  Configuration File
- If you get an empty page on the test client, make sure the left-hand side panel is open

