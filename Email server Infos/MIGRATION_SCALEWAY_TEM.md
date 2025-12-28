# Migration vers Scaleway TEM - Guide des changements

## Vue d'ensemble

Ce document décrit tous les changements nécessaires pour migrer de Google (Gmail) vers Scaleway TEM (Transactional Email) pour l'envoi d'emails.

## Changements dans le fichier Excel

### Fichier à modifier
- `runtime_dev/apps/delphes78/delphes78.xlsx` (et les autres fichiers Excel pour delphes91, delphes92, delphes94)
- Onglet : `email_config`

### Paramètres à modifier dans l'onglet `email_config`

| Paramètre | Ancienne valeur (Google) | Nouvelle valeur (Scaleway TEM) |
|-----------|-------------------------|-------------------------------|
| `smtp_server` | `smtp.gmail.com` | `smtp.tem.scaleway.com` |
| `smtp_port` | `587` | `587` (inchangé) |
| `password` | Mot de passe Gmail (`tubd yhuh fgiq hqrs`) | `64bc46a2-51f2-4152-9611-ddea51ad0709` (votre `SCW_SECRET_KEY`) |
| `hub_email_address` | `Athena.Delphes@gmail.com` | `ne-pas-repondre@athenadecisions.ai` (adresse "From" configurable) |
| `agent_email_address` | `pocagent78@gmail.com` | `pocagent78@gmail.com` (ou l'adresse email configurée dans Scaleway TEM) |

### Nouveau paramètre à ajouter

**IMPORTANT** : Il faut ajouter un nouveau champ `smtp_username` dans l'onglet `email_config` :

| Paramètre | Valeur |
|-----------|--------|
| `smtp_username` | `59c350ec-8be5-4b8b-8a4c-93db7f9690b3` (votre `SCW_DEFAULT_PROJECT_ID`) |

## Changements dans le code Python

### 1. Modifier `DistributionEmailConfig` pour ajouter `smtp_username`

**Fichier** : `src/backend/distribution/distribution_email/distribution_email_config.py`

Ajouter le champ `smtp_username` dans la classe `DistributionEmailConfig` :

```python
class DistributionEmailConfig(Config):
    hub_email_address: str
    agent_email_address: str
    case_field_email_address: str
    smtp_server: str
    smtp_username: str  # NOUVEAU : Username pour l'authentification SMTP
    password: str
    smtp_port: int
    send_email: bool
    email_templates: list[EmailTemplate]
```

### 2. Modifier la méthode `send_mail` pour utiliser `smtp_username`

**Fichier** : `src/backend/distribution/distribution_email/distribution_email.py`

**Ligne 311** : Remplacer :
```python
server.login(email_to_send.from_email_address, email_password)
```

Par :
```python
# Utiliser smtp_username si disponible, sinon utiliser l'adresse email (rétrocompatibilité)
smtp_username = getattr(email_config, 'smtp_username', None) or email_to_send.from_email_address
server.login(smtp_username, email_password)
```

### 3. Nettoyer le champ `smtp_username` dans `localized_app.py`

**Fichier** : `src/backend/backend/localized_app.py`

**Ligne 77** : Ajouter le nettoyage de `smtp_username` :

```python
email_config.smtp_server = clean_string(email_config.smtp_server)
email_config.smtp_username = clean_string(email_config.smtp_username)  # NOUVEAU
```

## Configuration Scaleway TEM

### Paramètres SMTP Scaleway TEM

- **Serveur SMTP** : `smtp.tem.scaleway.com`
- **Port** : `587` (TLS/STARTTLS)
- **Username** : `59c350ec-8be5-4b8b-8a4c-93db7f9690b3` (Project ID = `SCW_DEFAULT_PROJECT_ID`)
- **Password** : `64bc46a2-51f2-4152-9611-ddea51ad0709` (Secret Key = `SCW_SECRET_KEY`)

### Notes importantes

1. **Username vs Email** : Scaleway TEM utilise le Project ID comme username, pas l'adresse email
2. **Adresses email** : Les adresses `hub_email_address` et `agent_email_address` doivent être vérifiées/configurées dans Scaleway TEM
3. **Domaine vérifié** : Assurez-vous que le domaine utilisé pour les adresses email est vérifié dans Scaleway TEM
4. **Mot de passe SMTP** : 
   - **OUI, c'est bien `SCW_SECRET_KEY`** ! Pour Scaleway TEM, vous utilisez votre `SCW_SECRET_KEY` comme mot de passe SMTP
   - **Username SMTP** : Votre `SCW_DEFAULT_PROJECT_ID` (`59c350ec-8be5-4b8b-8a4c-93db7f9690b3`)
   - **Password SMTP** : Votre `SCW_SECRET_KEY` (`64bc46a2-51f2-4152-9611-ddea51ad0709`)
   - **Note** : Le mot de passe `tubd yhuh fgiq hqrs` était pour Gmail, pas pour Scaleway

## Variables d'environnement (optionnel)

Les variables d'environnement `.env` que vous avez mentionnées (`SCW_ACCESS_KEY`, `SCW_SECRET_KEY`, etc.) sont utilisées pour l'**API REST Scaleway**, mais **pas pour SMTP**.

### Authentification SMTP vs API REST

**Pour SMTP** (ce que nous utilisons ici) :
- `smtp_username` : Project ID = `SCW_DEFAULT_PROJECT_ID` (`59c350ec-8be5-4b8b-8a4c-93db7f9690b3`)
- `password` : Secret Key = `SCW_SECRET_KEY` (`64bc46a2-51f2-4152-9611-ddea51ad0709`)

**Pour l'API REST** (alternative, non utilisée ici) :
- `SCW_ACCESS_KEY` : Access Key ID
- `SCW_SECRET_KEY` : Secret Key (la même que pour SMTP)
- **Note** : Nous utilisons SMTP, donc pas besoin de réécrire le code pour l'API REST

## Checklist de migration

- [ ] 1. Modifier le fichier Excel `delphes78.xlsx` :
  - [ ] Mettre à jour `smtp_server` → `smtp.tem.scaleway.com`
  - [ ] Ajouter `smtp_username` → `59c350ec-8be5-4b8b-8a4c-93db7f9690b3` (votre `SCW_DEFAULT_PROJECT_ID`)
  - [ ] Mettre à jour `password` → `64bc46a2-51f2-4152-9611-ddea51ad0709` (votre `SCW_SECRET_KEY`)
  - [ ] Vérifier que `smtp_port` = `587`
  
- [ ] 2. Répéter pour les autres fichiers Excel (delphes91, delphes92, delphes94) si nécessaire

- [ ] 3. Modifier le code Python :
  - [ ] Ajouter `smtp_username: str` dans `DistributionEmailConfig`
  - [ ] Modifier `send_mail()` pour utiliser `smtp_username` au lieu de l'adresse email
  - [ ] Ajouter le nettoyage de `smtp_username` dans `localized_app.py`

- [ ] 4. Tester l'envoi d'email :
  - [ ] Vérifier que les emails partent correctement
  - [ ] Vérifier que les emails arrivent dans les boîtes de réception
  - [ ] Vérifier les logs pour s'assurer qu'il n'y a pas d'erreurs d'authentification

## Rétrocompatibilité

Le code modifié doit rester compatible avec les anciennes configurations qui n'ont pas `smtp_username`. Dans ce cas, on utilise l'adresse email comme username (comportement actuel).

## Dépannage

### Erreur "Permission denied" (535)

Si vous obtenez l'erreur `535 5.7.8 Permission denied` lors de l'authentification SMTP :

**Voir le guide détaillé** : `SCALEWAY_TEM_PERMISSIONS.md`

**Résumé rapide** :
1. **Créer une application IAM** dans **IAM & API keys** > **Applications**
2. **Créer une politique** dans **IAM & API keys** > **Politiques** :
   - Ajouter une règle avec le jeu de permissions **TEMFullAccess**
   - Attacher l'application créée comme principal
3. **Générer une clé API** pour cette application
4. Utiliser la **Secret Key** de cette nouvelle clé API comme mot de passe SMTP

3. **Vérifier le Project ID** :
   - Assurez-vous que le Project ID utilisé correspond bien au projet où TEM est activé
   - Vous pouvez le trouver dans **Transactional Email** > **Domain Overview**

4. **Vérifier que le domaine est vérifié** :
   - Le domaine doit être vérifié dans Scaleway TEM avant de pouvoir envoyer des emails
   - Allez dans **Transactional Email** > **Domains** et vérifiez le statut

### Test de connexion SMTP

Pour tester manuellement la connexion SMTP :

```python
import smtplib

smtp_server = "smtp.tem.scaleway.com"
smtp_port = 587
username = "59c350ec-8be5-4b8b-8a4c-93db7f9690b3"  # Project ID
password = "64bc46a2-51f2-4152-9611-ddea51ad0709"  # Secret Key

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.set_debuglevel(1)  # Pour voir les détails
    server.starttls()
    server.login(username, password)
    print("Connexion réussie!")
    server.quit()
except Exception as e:
    print(f"Erreur: {e}")
```

## Support

En cas de problème :
1. Vérifier les logs du serveur backend (avec `set_debuglevel(1)` pour plus de détails)
2. Vérifier la configuration dans Scaleway TEM (permissions, domaine vérifié)
3. Tester la connexion SMTP manuellement avec le script `test_scaleway_smtp.py`
4. Consulter la documentation Scaleway : https://www.scaleway.com/en/docs/transactional-email/

### Erreur "Permission denied" persistante

Si l'erreur `535 5.7.8 Permission denied` persiste malgré une politique correcte :

1. **Vérifier le Project ID** :
   - Le Project ID utilisé comme `smtp_username` doit être celui du projet où TEM est activé
   - Allez dans **Transactional Email** → **Domain Overview** pour trouver le bon Project ID
   - Ne pas confondre avec l'Organization ID

2. **Vérifier que la politique est bien attachée** :
   - Allez dans **IAM & API keys** → **Applications** → Votre application → **Politiques**
   - La politique avec `TEMFullAccess` doit être listée
   - Vérifiez que le projet ciblé par la politique correspond au projet où TEM est activé

3. **Contacter le support Scaleway** :
   - Si le problème persiste, contactez le support Scaleway avec :
     - Project ID utilisé
     - ID de la clé API
     - Message d'erreur complet (535 5.7.8 Permission denied)
     - Confirmation que le domaine est vérifié
     - Confirmation que la politique TEMFullAccess est attachée

