#!/usr/bin/env python3
"""
Script de démonstration pour tester smtp4dev
Envoie un email de test qui sera capturé par smtp4dev
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_test_email():
    """Envoie un email de test à smtp4dev"""
    
    # Configuration SMTP pour smtp4dev
    smtp_server = "localhost"
    smtp_port = 25  # ou 2525
    
    # Informations de l'email
    from_email = "demo@trusted-services.local"
    to_email = "joel@milgram.fr"
    subject = f"Email de test smtp4dev - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Création du message
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    
    # Corps du message HTML
    body_html = """
    <html>
      <head></head>
      <body>
        <h1 style="color: #2c3e50;">🎉 Démonstration smtp4dev</h1>
        <p>Ceci est un email de test envoyé à <strong>smtp4dev</strong>.</p>
        <p>L'email a été capturé et n'a pas été envoyé réellement.</p>
        <hr>
        <p><em>Envoyé le: {timestamp}</em></p>
        <p>Vous pouvez voir cet email dans l'interface web de smtp4dev :</p>
        <p><a href="http://localhost:5001">http://localhost:5001</a></p>
      </body>
    </html>
    """.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    message.attach(MIMEText(body_html, "html", "utf-8"))
    
    try:
        print(f"📧 Envoi d'un email de test à smtp4dev...")
        print(f"   Serveur: {smtp_server}:{smtp_port}")
        print(f"   De: {from_email}")
        print(f"   À: {to_email}")
        
        # Connexion au serveur SMTP (smtp4dev n'a pas besoin d'authentification)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Envoi de l'email
            server.sendmail(from_email, to_email, message.as_string())
        
        print("✅ Email envoyé avec succès!")
        print(f"\n🌐 Ouvrez votre navigateur sur http://localhost:5001 pour voir l'email capturé")
        return True
        
    except ConnectionRefusedError:
        print("❌ Erreur: Impossible de se connecter au serveur SMTP")
        print("   Assurez-vous que smtp4dev est démarré:")
        print("   docker-compose -f docker-compose.mail-server.yml up -d")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")
        return False

if __name__ == "__main__":
    send_test_email()

