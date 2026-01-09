#!/usr/bin/env python
"""
Script minimal pour tester l'envoi d'email via Scaleway TEM
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration Scaleway TEM
SMTP_SERVER = "smtp.tem.scaleway.com"
SMTP_PORT = 587
SMTP_USERNAME = "59c350ec-8be5-4b8b-8a4c-93db7f9690b3"  # Project ID
SMTP_PASSWORD = "64bc46a2-51f2-4152-9611-ddea51ad0709"  # Secret Key de la clé API

# Adresses email
FROM_EMAIL = "ne-pas-repondre@mail.athenadecisions.ai"
TO_EMAIL = "j@milgram.fr"

# Contenu de l'email
SUBJECT = "Test SMTP Scaleway TEM"
BODY_TEXT = """
Ceci est un test d'envoi d'email via Scaleway Transactional Email (TEM).

Configuration utilisée:
- Serveur: smtp.tem.scaleway.com:587
- From: ne-pas-repondre@mail.athenadecisions.ai
- To: j@milgram.fr

Si vous recevez cet email, la configuration SMTP fonctionne correctement!
"""

def send_email():
    """Envoie un email de test via Scaleway TEM"""
    
    print("=" * 60)
    print("Test d'envoi d'email via Scaleway TEM")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Serveur SMTP: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"  Username (Project ID): {SMTP_USERNAME}")
    print(f"  Password (Secret Key): {SMTP_PASSWORD[:10]}...")
    print(f"  From: {FROM_EMAIL}")
    print(f"  To: {TO_EMAIL}")
    print(f"  Subject: {SUBJECT}")
    print("=" * 60)
    print()
    
    try:
        # Créer le message email
        print("1. Création du message email...")
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = SUBJECT
        
        # Ajouter le corps du message
        msg.attach(MIMEText(BODY_TEXT, 'plain', 'utf-8'))
        print("   ✓ Message créé")
        
        # Connexion au serveur SMTP
        print("2. Connexion au serveur SMTP...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        print(f"   ✓ Connecté à {SMTP_SERVER}:{SMTP_PORT}")
        
        # Activer le mode debug pour voir les détails (optionnel)
        # Décommentez la ligne suivante pour voir les détails SMTP
        # server.set_debuglevel(1)
        
        # Démarrer TLS
        print("3. Démarrage de la connexion TLS...")
        server.starttls()
        print("   ✓ TLS activé")
        
        # Authentification
        print("4. Authentification...")
        print(f"   Username: {SMTP_USERNAME}")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        print("   ✓ Authentification réussie!")
        
        # Envoi de l'email
        print("5. Envoi de l'email...")
        server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_bytes())
        print("   ✓ Email envoyé avec succès!")
        
        # Fermeture de la connexion
        server.quit()
        print()
        print("=" * 60)
        print("✓ Test réussi! L'email a été envoyé.")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print()
        print("=" * 60)
        print("✗ ERREUR D'AUTHENTIFICATION")
        print("=" * 60)
        print(f"Erreur: {e}")
        print()
        print("Vérifiez:")
        print("  - Le Project ID est correct et correspond au projet où TEM est activé")
        print("  - La Secret Key est correcte (celle de la nouvelle clé API)")
        print("  - La clé API a les permissions TEMFullAccess")
        print("  - La politique est bien attachée à l'application IAM")
        print("  - Le domaine 'athenadecisions.ai' est vérifié dans Scaleway TEM")
        return False
        
    except smtplib.SMTPException as e:
        print()
        print("=" * 60)
        print("✗ ERREUR SMTP")
        print("=" * 60)
        print(f"Erreur: {e}")
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ ERREUR")
        print("=" * 60)
        print(f"Type: {type(e).__name__}")
        print(f"Erreur: {e}")
        return False


if __name__ == "__main__":
    success = send_email()
    exit(0 if success else 1)

