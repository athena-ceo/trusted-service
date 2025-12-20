# Services Email pour la Production

Ce document liste les options recommandées pour l'envoi d'emails transactionnels en production.

## 🎯 Services Recommandés

### 0. **Scaleway TEM (Transactional Email)** ⭐ Recommandé si vous utilisez Scaleway
- **Prix** : 
  - **Essential** : 300 emails/mois inclus, puis 0,25€ par tranche de 1000 emails
  - **Scale** : 100 000 emails/mois inclus, puis 0,20€ par tranche de 1000 emails
- **Avantages** :
  - ✅ **Souveraineté européenne** : Données hébergées en Europe (RGPD-friendly)
  - ✅ **Intégration native** : Si vous utilisez déjà Scaleway, intégration simplifiée
  - ✅ **Haute délivrabilité** : Optimisé pour emails transactionnels
  - ✅ **Évolutivité** : Gère les pics de charge
  - ✅ **Sécurité** : Centres de données européens certifiés
  - ✅ **Tableau de bord analytique** : Rapports détaillés et alertes
  - ✅ **API REST et SMTP** : Compatible avec votre code existant
- **Configuration SMTP** :
  - Serveur : `smtp.tem.scw.cloud` (à vérifier dans votre console Scaleway)
  - Port : `587` (TLS) ou `465` (SSL)
  - Utilisateur : Votre clé API TEM
  - Mot de passe : Votre secret API TEM
- **Plans** :
  - **Essential** : 5 domaines, 300 emails/mois, 1 webhook/domaine
  - **Scale** : Domaines illimités, 100 000 emails/mois, webhooks illimités, IP dédiée, SLA 99,9%
- **Site** : https://www.scaleway.com/fr/transactional-email-tem/
- **Note** : Idéal si vous hébergez déjà sur Scaleway pour une intégration simplifiée

### 1. **SendGrid** (Recommandé pour débuter)
- **Prix** : Gratuit jusqu'à 100 emails/jour, puis à partir de ~15€/mois
- **Avantages** :
  - Interface simple et intuitive
  - Excellente délivrabilité
  - API REST et SMTP
  - Statistiques détaillées
  - Support français disponible
- **Configuration SMTP** :
  - Serveur : `smtp.sendgrid.net`
  - Port : `587` (TLS) ou `465` (SSL)
  - Utilisateur : `apikey`
  - Mot de passe : Votre clé API SendGrid
- **Site** : https://sendgrid.com

### 2. **Mailgun**
- **Prix** : Gratuit jusqu'à 5000 emails/mois (3 mois), puis ~35€/mois
- **Avantages** :
  - Très bonne délivrabilité
  - API puissante
  - Logs détaillés
  - Support webhooks
- **Configuration SMTP** :
  - Serveur : `smtp.mailgun.org`
  - Port : `587` (TLS) ou `465` (SSL)
  - Utilisateur : Votre domaine Mailgun
  - Mot de passe : Votre clé API Mailgun
- **Site** : https://www.mailgun.com

### 3. **Amazon SES** (Recommandé pour AWS)
- **Prix** : ~0,10$ pour 1000 emails (très économique)
- **Avantages** :
  - Très économique à grande échelle
  - Intégration native AWS
  - Excellente délivrabilité
  - Scalable
- **Configuration SMTP** :
  - Serveur : `email-smtp.{region}.amazonaws.com` (ex: `email-smtp.eu-west-1.amazonaws.com`)
  - Port : `587` (TLS) ou `465` (SSL)
  - Utilisateur : Votre clé d'accès SMTP
  - Mot de passe : Votre secret SMTP
- **Site** : https://aws.amazon.com/ses/

### 4. **Postmark**
- **Prix** : Gratuit jusqu'à 100 emails/mois, puis ~15€/mois
- **Avantages** :
  - Excellente délivrabilité
  - Spécialisé emails transactionnels
  - Support réactif
  - Interface claire
- **Configuration SMTP** :
  - Serveur : `smtp.postmarkapp.com`
  - Port : `587` (TLS) ou `2525` (TLS)
  - Utilisateur : Votre Server API Token
  - Mot de passe : Votre Server API Token (même valeur)
- **Site** : https://postmarkapp.com

### 5. **Brevo (ex-Sendinblue)** - Recommandé pour la France
- **Prix** : Gratuit jusqu'à 300 emails/jour, puis à partir de ~25€/mois
- **Avantages** :
  - Entreprise française (RGPD-friendly)
  - Interface en français
  - Support français
  - Bonne délivrabilité
- **Configuration SMTP** :
  - Serveur : `smtp-relay.brevo.com`
  - Port : `587` (TLS) ou `465` (SSL)
  - Utilisateur : Votre email Brevo
  - Mot de passe : Votre clé SMTP Brevo
- **Site** : https://www.brevo.com

## 🔧 Configuration dans votre Projet

Votre code utilise déjà SMTP standard, donc vous pouvez utiliser n'importe lequel de ces services en modifiant simplement la configuration dans votre fichier Excel :

```python
# Exemple de configuration pour Scaleway TEM
smtp_server = "smtp.tem.scw.cloud"  # À vérifier dans votre console Scaleway
smtp_port = 587
password = "votre_secret_api_tem"  # Votre secret API TEM
from_email_address = "noreply@votre-domaine.com"  # Doit être vérifié

# Exemple de configuration pour SendGrid
smtp_server = "smtp.sendgrid.net"
smtp_port = 587
password = "SG.xxxxxxxxxxxxx"  # Votre clé API SendGrid
from_email_address = "noreply@votre-domaine.com"  # Doit être vérifié
```

## 📋 Comparaison Rapide

| Service | Gratuit | Prix/Mois | Délivrabilité | Support FR | Recommandation |
|---------|---------|-----------|---------------|------------|----------------|
| **Scaleway TEM** | 300/mois | 0,25€/1000 | ⭐⭐⭐⭐⭐ | ✅✅ | Scaleway |
| **SendGrid** | 100/jour | ~15€ | ⭐⭐⭐⭐⭐ | ✅ | Débutant |
| **Brevo** | 300/jour | ~25€ | ⭐⭐⭐⭐ | ✅✅ | France |
| **Mailgun** | 5000/mois* | ~35€ | ⭐⭐⭐⭐⭐ | ✅ | Avancé |
| **Amazon SES** | Payant | ~0,10$/1000 | ⭐⭐⭐⭐⭐ | ❌ | AWS |
| **Postmark** | 100/mois | ~15€ | ⭐⭐⭐⭐⭐ | ✅ | Transactionnel |

*Gratuit pendant 3 mois seulement

## ⚠️ Important pour la Production

1. **Vérification du domaine** : La plupart des services nécessitent de vérifier votre domaine d'envoi
2. **Authentification SPF/DKIM** : Configurez les enregistrements DNS pour améliorer la délivrabilité
3. **Rate limiting** : Respectez les limites d'envoi pour éviter la blacklist
4. **Monitoring** : Surveillez les taux de rebond et de spam
5. **Sécurité** : Ne commitez jamais les clés API dans le code, utilisez des variables d'environnement

## 🔐 Bonnes Pratiques

- Utilisez des variables d'environnement pour les credentials
- Implémentez un système de retry pour les échecs temporaires
- Loggez tous les envois d'emails
- Surveillez les taux de rebond
- Utilisez un domaine dédié pour l'envoi (pas votre domaine principal)

## 🚀 Migration depuis Gmail

Si vous utilisez actuellement Gmail SMTP, voici pourquoi migrer :

- ❌ Gmail limite à 500 emails/jour
- ❌ Risque de suspension de compte
- ❌ Pas optimisé pour emails transactionnels
- ❌ Pas de statistiques détaillées
- ✅ Les services ci-dessus sont conçus pour la production

