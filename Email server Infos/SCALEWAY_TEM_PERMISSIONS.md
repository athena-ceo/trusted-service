# Configuration des permissions Scaleway TEM

## Guide étape par étape

Pour utiliser Scaleway TEM avec SMTP, vous devez créer une **application IAM** avec une **politique** qui accorde les permissions `TEMFullAccess`, puis générer une **clé API** pour cette application.

### Étape 1 : Créer une application IAM

1. Connectez-vous à la [console Scaleway](https://console.scaleway.com/)
2. Dans le menu supérieur, cliquez sur **IAM & API keys** (ou **IAM & Clés API**)
3. Allez dans l'onglet **Applications**
4. Cliquez sur **+ Créer une application** (ou **+ Create application**)
5. Remplissez :
   - **Nom** : Par exemple `Delphes TEM` ou `Transactional Email`
   - **Description** : Optionnel, par exemple "Application pour l'envoi d'emails transactionnels"
6. Cliquez sur **Créer une application**

### Étape 2 : Créer une politique avec TEMFullAccess

1. Toujours dans **IAM & API keys**, allez dans l'onglet **Politiques** (ou **Policies**)
2. Cliquez sur **+ Créer une politique** (ou **+ Create policy**)
3. Remplissez les informations :
   - **Nom** : Par exemple `TEMFullAccessPolicy` ou `Delphes TEM Policy`
   - **Description** : Optionnel
4. Dans la section **Règles** (ou **Rules**), cliquez sur **Ajouter une règle** (ou **Add rule**)
5. Configurez la règle :
   - **Accès aux ressources** (Resource access) : 
     - Sélectionnez votre projet spécifique OU
     - Sélectionnez **Tous les projets actuels** (All current projects) si vous voulez que ça s'applique à tous vos projets
   - **Jeu de permissions** (Permission set) : 
     - Dans la liste déroulante, cherchez et sélectionnez **TEMFullAccess**
     - Si vous ne le voyez pas, essayez de taper "TEM" dans la recherche
6. Dans la section **Principal** (ou **Principal**) :
   - Cliquez sur **Ajouter un principal** (ou **Add principal**)
   - Sélectionnez **Application**
   - Choisissez l'application IAM que vous avez créée à l'étape 1
7. Cliquez sur **Créer une politique** (ou **Create policy**)

### Étape 3 : Générer une clé API pour l'application

1. Retournez dans l'onglet **Applications**
2. Cliquez sur l'application IAM que vous avez créée à l'étape 1
3. Allez dans l'onglet **Clés API** (ou **API Keys**)
4. Cliquez sur **+ Générer une clé API** (ou **+ Generate API key**)
5. Remplissez les informations :
   - **Description** : Par exemple "Clé API SMTP pour Delphes"
   - **Date d'expiration** : Optionnel (laissez vide pour pas d'expiration)
   - **Projet préféré pour Object Storage** : Sélectionnez votre projet si nécessaire
6. Cliquez sur **Générer une clé API** (ou **Generate API key**)
7. **IMPORTANT** : Copiez immédiatement :
   - **Access Key ID** : C'est votre `SCW_ACCESS_KEY`
   - **Secret Key** : C'est votre `SCW_SECRET_KEY` (mot de passe SMTP)
   - ⚠️ **La Secret Key ne sera affichée qu'une seule fois !**

### Étape 4 : Mettre à jour votre configuration

Une fois la clé API générée, mettez à jour votre fichier Excel avec :

| Paramètre | Valeur |
|-----------|--------|
| `smtp_username` | Votre **Project ID** (ex: `59c350ec-8be5-4b8b-8a4c-93db7f9690b3`) |
| `password` | La **Secret Key** de la nouvelle clé API générée |

## Vérification

Pour vérifier que tout fonctionne :

1. Vérifiez que votre politique est bien attachée à l'application :
   - Allez dans **Applications** > Votre application > Onglet **Politiques**
   - Vous devriez voir votre politique listée

2. Testez la connexion SMTP avec le script Python :
   ```bash
   source .venv/bin/activate
   export PYTHONPATH=.
   python src/backend/distribution/distribution_email/distribution_email.py
   ```

## Notes importantes

- **Project ID** : Le `smtp_username` doit être le **Project ID** où TEM est activé, pas l'Organization ID
- **Secret Key** : Utilisez la **Secret Key** de la clé API (pas l'Access Key ID) comme mot de passe SMTP
- **Domaine vérifié** : Assurez-vous que votre domaine (`athenadecisions.ai`) est vérifié dans **Transactional Email** > **Domains**

## Si vous ne trouvez pas TEMFullAccess

Si le jeu de permissions `TEMFullAccess` n'apparaît pas dans la liste :

1. Vérifiez que vous avez accès au service Transactional Email
2. Essayez de chercher "TEM" ou "Transactional" dans la barre de recherche des jeux de permissions
3. Les permissions peuvent aussi être nommées différemment selon la région/langue :
   - `TEMFullAccess`
   - `TransactionnalEmailFullAccess`
   - Ou simplement les permissions individuelles : `tem:read` et `tem:write`

## Alternative : Permissions individuelles

Si `TEMFullAccess` n'est pas disponible, vous pouvez créer une politique personnalisée avec :
- `tem:read` - Pour lire les statistiques
- `tem:write` - Pour envoyer des emails

Mais `TEMFullAccess` est recommandé pour simplifier.

