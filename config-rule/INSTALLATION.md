# Installation Guide - Ruleflow Editor

## Prérequis

- Node.js 18+ et npm
- Python 3.11+
- Le backend Trusted Services doit être en cours d'exécution

## Installation

### 1. Installer les dépendances frontend

```bash
cd config-rule
npm install
```

### 2. Configuration du backend

Le backend est déjà intégré dans le projet principal. Les fichiers se trouvent dans :
- `src/backend/ruleflow/ruleflow_parser.py` - Parser pour analyser les fichiers decision_engine.py
- `src/backend/ruleflow/ruleflow_api.py` - API REST pour l'éditeur

L'API est automatiquement incluse dans le backend FastAPI via `src/backend/backend/rest/main.py`.

### 3. Démarrer le backend

Assurez-vous que le backend FastAPI est en cours d'exécution sur le port 8002 (ou modifiez `next.config.ts` pour changer l'URL du proxy).

### 4. Démarrer le frontend

```bash
cd config-rule
npm run dev
```

Le frontend sera accessible sur http://localhost:3001

## Utilisation

1. **Sélectionner un runtime** : Choisissez un répertoire runtime dans le menu déroulant
2. **Sélectionner une app** : Choisissez une application (ou créez-en une nouvelle)
3. **Éditer le ruleflow** :
   - Ajouter/supprimer/déplacer des packages
   - Modifier les conditions d'exécution des packages
   - Ajouter/supprimer/déplacer des règles
   - Éditer le code des règles
   - Modifier les conditions d'exécution des règles

## Structure des fichiers

- Les fichiers `decision_engine.py` sont automatiquement analysés et régénérés
- Les modifications sont sauvegardées directement dans les fichiers Python
- Le format du code est préservé autant que possible

## Dépannage

### Le backend ne répond pas

Vérifiez que :
1. Le backend FastAPI est en cours d'exécution
2. Le port dans `next.config.ts` correspond au port du backend
3. Les routes `/api/v1/ruleflow/*` sont accessibles

### Erreurs d'import Python

Vérifiez que :
1. Les fichiers dans `src/backend/ruleflow/` sont présents
2. Le router est bien inclus dans `src/backend/backend/rest/main.py`
3. Les imports fonctionnent correctement

### Erreurs frontend

Vérifiez que :
1. Toutes les dépendances sont installées (`npm install`)
2. Le serveur de développement est en cours d'exécution
3. Les fichiers TypeScript compilent sans erreur



