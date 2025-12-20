# Serveur Email SMTP4Dev

Serveur SMTP de développement qui capture tous les emails sans les envoyer réellement.

## 🚀 Démarrage

```bash
docker compose -f docker-compose.mail-server.yml up -d
```

## 🛑 Arrêt

```bash
docker compose -f docker-compose.mail-server.yml down
```

## 📧 Configuration SMTP

Pour utiliser smtp4dev dans votre application :

- **Serveur SMTP** : `localhost` (ou `smtp4dev` depuis un autre conteneur Docker)
- **Port** : `25` ou `2525`
- **Authentification** : Aucune requise (smtp4dev accepte tout)
- **TLS/STARTTLS** : Optionnel (fonctionne avec ou sans)

## 🌐 Interface Web

L'interface web est accessible sur : **http://localhost:5001**

Vous pouvez y voir tous les emails capturés, leur contenu HTML, les en-têtes, etc.

## 🧪 Test rapide

Un script de démonstration est disponible :

```bash
python3 demo_smtp4dev.py
```

Ce script envoie un email de test qui sera capturé par smtp4dev.

## 📝 Notes

- smtp4dev ne stocke pas les emails de manière persistante (ils sont perdus au redémarrage)
- Tous les emails sont capturés, aucune authentification n'est requise
- Idéal pour le développement et les tests locaux

