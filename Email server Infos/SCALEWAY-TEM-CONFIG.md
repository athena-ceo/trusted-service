# Configuration Scaleway TEM avec athenadecisions.com

## 🔍 Pourquoi un nom de domaine est nécessaire ?

Scaleway TEM (et tous les services d'email transactionnel professionnels) nécessitent un nom de domaine pour plusieurs raisons critiques :

### 1. **Authentification et Réputation**
- Le domaine permet de prouver que vous êtes le propriétaire légitime
- Évite l'usurpation d'identité (spoofing)
- Construit la réputation de votre domaine pour une meilleure délivrabilité

### 2. **Configuration DNS (SPF, DKIM, DMARC)**
- **SPF** : Indique quels serveurs sont autorisés à envoyer des emails pour votre domaine
- **DKIM** : Signature cryptographique qui garantit l'authenticité de l'email
- **DMARC** : Politique de protection contre le phishing et le spam

### 3. **Délivrabilité**
- Les emails envoyés depuis votre propre domaine ont un taux de délivrabilité bien supérieur
- Évite que vos emails soient classés comme spam
- Les boîtes de réception (Gmail, Outlook, etc.) font confiance aux emails authentifiés

### 4. **Professionnalisme**
- Les emails viennent de `noreply@athenadecisions.com` plutôt que `noreply@gmail.com`
- Image de marque plus professionnelle
- Confiance accrue des destinataires

## 📝 Quel domaine indiquer dans Scaleway TEM ?

Vous devez indiquer : **`athenadecisions.com`**

C'est votre domaine principal. Scaleway TEM va :
1. Vérifier que vous êtes propriétaire du domaine
2. Générer les enregistrements DNS à ajouter
3. Vous permettre d'envoyer des emails depuis n'importe quelle adresse `@athenadecisions.com`

## 🎯 Adresses email recommandées

Une fois le domaine configuré, vous pourrez utiliser des adresses comme :

- `noreply@athenadecisions.com` - Pour les emails automatiques (recommandé)
- `contact@athenadecisions.com` - Pour les réponses
- `support@athenadecisions.com` - Pour le support
- `delphes@athenadecisions.com` - Pour l'application Delphes
- `hub@athenadecisions.com` - Pour le hub (remplace Athena.Delphes@gmail.com)

## 🔧 Configuration dans Scaleway TEM

### Étape 1 : Ajouter le domaine dans Scaleway

1. Connectez-vous à votre console Scaleway
2. Allez dans **Transactional Email (TEM)**
3. Cliquez sur **"Add Domain"** ou **"Ajouter un domaine"**
4. Entrez : `athenadecisions.com`
5. Sélectionnez votre plan (Essential ou Scale)

### Étape 2 : Vérification du domaine

Scaleway va vous demander de vérifier la propriété du domaine. Vous aurez deux options :

**Option A : Enregistrement TXT** (Recommandé)
- Scaleway génère un enregistrement TXT à ajouter dans votre DNS
- Exemple : `scw-verify=abc123def456...`
- Ajoutez-le dans votre gestionnaire DNS

**Option B : Fichier HTML**
- Téléchargez un fichier HTML
- Placez-le à la racine de votre site web
- Scaleway vérifie l'accès au fichier

### Étape 3 : Configuration DNS (SPF, DKIM, DMARC)

Après vérification, Scaleway vous donnera les enregistrements DNS à ajouter :

#### Enregistrement SPF
```
Type: TXT
Nom: @ (ou athenadecisions.com)
Valeur: v=spf1 include:tem.scw.cloud ~all
```

#### Enregistrement DKIM
```
Type: TXT
Nom: scw._domainkey (ou scw._domainkey.athenadecisions.com)
Valeur: [Généré par Scaleway - très long]
```

#### Enregistrement DMARC (Optionnel mais recommandé)
```
Type: TXT
Nom: _dmarc (ou _dmarc.athenadecisions.com)
Valeur: v=DMARC1; p=none; rua=mailto:dmarc@athenadecisions.com
```

### Étape 4 : Génération des clés API

Une fois le domaine vérifié et les DNS configurés :

1. Allez dans **API Keys** ou **Clés API**
2. Créez une nouvelle clé API SMTP
3. Notez :
   - **Serveur SMTP** : `smtp.tem.scw.cloud` (ou celui indiqué)
   - **Port** : `587` (TLS) ou `465` (SSL)
   - **Username** : Votre clé API
   - **Password** : Votre secret API

## 🔄 Mise à jour de votre configuration

Une fois Scaleway TEM configuré, mettez à jour votre fichier Excel de configuration :

| Paramètre | Ancienne valeur | Nouvelle valeur |
|-----------|----------------|-----------------|
| **hub_email_address** | `Athena.Delphes@gmail.com` | `hub@athenadecisions.com` ou `noreply@athenadecisions.com` |
| **agent_email_address** | `pref-delphes-sejour@yvelines.gouv.fr,...` | (Conserver ou adapter) |
| **smtp_server** | `smtp.gmail.com` | `smtp.tem.scw.cloud` |
| **password** | `xxxx xxxx xxxx xxxx` | Votre secret API Scaleway TEM |
| **smtp_port** | `587` | `587` (reste identique) |
| **send_email** | `True` | `True` |

## ⏱️ Délai de propagation DNS

- **Vérification du domaine** : Quelques minutes à quelques heures
- **Propagation SPF/DKIM** : 24-48 heures maximum
- **Activation complète** : Généralement dans les 24 heures

## ✅ Vérification

Une fois configuré, testez avec votre script de démo :

```python
# Modifiez demo_smtp4dev.py temporairement pour tester Scaleway
smtp_server = "smtp.tem.scw.cloud"
smtp_port = 587
from_email = "noreply@athenadecisions.com"
```

## 🚨 Points d'attention

1. **Ne supprimez pas les enregistrements DNS** une fois configurés
2. **Conservez vos clés API en sécurité** (variables d'environnement)
3. **Testez d'abord avec quelques emails** avant de passer en production
4. **Surveillez les statistiques** dans le tableau de bord Scaleway
5. **Respectez les limites** de votre plan pour éviter la suspension

## 📚 Ressources

- Documentation Scaleway TEM : https://www.scaleway.com/fr/docs/transactional-email/
- Console Scaleway : https://console.scaleway.com/

