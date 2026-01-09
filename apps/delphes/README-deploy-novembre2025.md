# 🚀 Guide de Déploiement Delphes - Novembre 2025

> **Application de modernisation de l'accueil des étrangers dans les préfectures françaises**

Ce guide détaille la procédure *actuelle* complète de déploiement de l'application Delphes en production, depuis la préparation côté développement jusqu'au déploiement côté serveur.

## 📋 Prérequis

- ✅ Accès au repository Git
- ✅ Droits Docker sur le serveur
- ✅ Accès SSH au serveur de production

---

## 💻 Phase 1 : Préparation côté Laptop

### 1.1 🏗️ Build du Frontend

Naviguez vers le répertoire de l'application et lancez le build :

```bash
cd <wherever>/trusted-service/apps/delphes
./build-frontend.sh
```

**ℹ️ Note :** Le script va automatiquement :

- Générer une nouvelle image Docker
- La pousser vers le registry
- Mettre à jour `deploy/compose/docker-compose.delphes-frontend-prod.yml`

### 1.2 📄 Configuration Delphes

Mettre à jour les fichier de configuration `delphes*.xlsx` de la prod :

**⚠️ Important :** Conservez la configuration email existante dans le fichier copié.

#### Configuration Email Requise

| Paramètre                         | Valeur                                                                                                                                                   |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **hub_email_address**        | [ne-pas-repondre@mail.athendadecisions.ai](mailto:ne-pas-repondre@mail.athendadecisions.ai)                                                                 |
| **agent_email_address**      | [pref-delphes-sejour@yvelines.gouv.fr,pref-delphes-asile@yvelines.gouv.fr](mailto:pref-delphes-sejour@yvelines.gouv.fr,pref-delphes-asile@yvelines.gouv.fr) |
| **case_field_email_address** | `adresse_mail`                                                                                                                                         |
| **smtp_server**              | `smtp.tem.scaleway.com`                                                                                                                                |
| **password**                 | `xxxx-xxxx-xxxx-xxxx`                                                                                                                                  |
| **smtp_port**                | `587`                                                                                                                                                  |
| **send_email**               | `True`                                                                                                                                                 |

### 1.3 ⚙️ Règles de décision

Mettre à jour les règles de décision de production.

### 1.4 🔄 Synchronisation Git

Poussez toutes les modifications vers le repository :

```bash
git add .
git commit -m "🚀 Déploiement production - $(date +%Y-%m-%d)"
git push origin main
```

---

## 🖥️ Phase 2 : Déploiement côté Serveur

* [ ] 2.1 🛑 Arrêt du Service

Connectez-vous au serveur et arrêtez les conteneurs existants :

```bash
cd /data/demos/trusted-service/apps/delphes
docker-compose -f deploy/compose/docker-compose.delphes-frontend-prod.yml down
```

**⚠️ Important :** Le conteneur doit être arrêté avant `git pull` car `deploy/compose/docker-compose.delphes-frontend-prod.yml` change à chaque build.

### 2.2 📊 Vérification du Statut Git

Vérifiez l'état du repository avant mise à jour :

```bash
git status
```

### 2.3 🔄 Mise à Jour du Code

**Option A : Mise à jour propre (recommandée)**

```bash
git pull origin main
```

**Option B : Reset complet (si conflits)**

```bash
git reset --hard HEAD
git pull origin main
```

### 2.4 🚀 Déploiement de la Nouvelle Version

Démarrez la nouvelle version de l'application :

```bash
cd /data/demos/trusted-service/apps/delphes
docker-compose -f deploy/compose/docker-compose.delphes-frontend-prod.yml up -d
```

---

## 🔧 Phase 3 : Configuration Spéciale

### 3.1 📊 Si le fichier `delphes.xlsx` a changé

En cas de modification de la configuration métier, redémarrez le service API :

```bash
sudo systemctl restart trusted-services-api
```

**ℹ️ Note :** Cette étape n'est nécessaire que si le code backend ou si des configurations ont été modifiés.

### 3.2 📊 Relancer le client test Streamlit

Si le code Python a changé, il faut redémarrer le service Test client :

```bash
sudo systemctl restart trusted-demo
```

---

## 📊 Monitoring et Vérifications

### Vérification du déploiement

```bash
# Vérifier que les conteneurs tournent
docker-compose -f deploy/compose/docker-compose.delphes-frontend-prod.yml ps

# Consulter les logs
docker-compose -f deploy/compose/docker-compose.delphes-frontend-prod.yml logs -f frontend

# Tester l'application
https://delphes.athenadecisions.com/
```

---

## **🎉 Déploiement réussi ! L'application Delphes est maintenant en production.**

*Guide mis à jour le : 5 novembre 2025*

</div>
