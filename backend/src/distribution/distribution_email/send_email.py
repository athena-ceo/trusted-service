import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

from backend.src.distribution.distribution_email.email2 import Email
from backend.src.distribution.distribution_email.distribution_email_configuration import DistributionEmailConfiguration


def create_mailto_link(email: str, subject: str, body: str) -> str:
    # Encode subject and body to be URL-safe
    from urllib.parse import quote

    mailto: str = f"mailto:{email}"

    # Add query parameters
    query: list[Any] = []
    if subject:
        query.append(f"subject={quote(subject)}")
    if body:
        query.append(f"body={quote(body)}")

    if query:
        mailto += "?" + "&".join(query)

    # Return the complete mailto link as an HTML anchor
    return f'<a href="{mailto}">{email}</a>'


def build_body(body: str, email_mail_to: Optional[Email]) -> str:
    body = "<html> <blockquote>" + body

    if email_mail_to is not None:
        mailto_link = create_mailto_link(
            email=email_mail_to.to_email_address,
            subject=email_mail_to.subject,
            body=email_mail_to.body,
        )
        body += "<br>Répondre à " + mailto_link

    body += "</blockquote> </html>"

    return body


def send_mail(email_configuration: DistributionEmailConfiguration,
              email_to_send: Email,
              email_mail_to: Optional[Email]) -> None:
    email_password = email_configuration.password
    smtp_server = email_configuration.smtp_server
    smtp_port = email_configuration.smtp_port

    # Email content

    # Create email
    message = MIMEMultipart()
    message["From"] = email_to_send.from_email_address
    message["To"] = email_to_send.to_email_address
    message["Subject"] = email_to_send.subject

    body = build_body(body=email_to_send.body, email_mail_to=email_mail_to)

    print("--- body ---")
    print(body)
    print("------------")

    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Start TLS encryption
            server.login(email_to_send.from_email_address, email_password)  # Login with secrets
            server.sendmail(
                email_to_send.from_email_address, email_to_send.to_email_address, message.as_string()
            )  # Send email
        print("Envoi de l'email réussi!")
    except Exception as e:
        print(f"Envoi de l'email échoué: {e}")


def main():
    body = """
<br><p style="font-weight: bold; color: blue;">1 - Données du cas</p><b>Intention</b>: expiration_d_une_api<br><b>Date de la demande JJ/MM/AAAA</b>: 21/05/2025<br><b>Département de la demande</b>: 78<br><b>Nom</b>: Doe<br><b>
Prénom</b>: John<br><b>Adresse mail</b>: johndoe@outlook<br><b>Numéro AGDREF</b>: <br><b>Date d'expiration de l'API</b>: 11/10/2024<br><b>Mention de risque sur l'emploi</b>: True<br><br><p style="font-weight: bold; color: blue;">2
 - Demande rédigée par le demandeur</p><table border="1" cellpadding="10"><tr><td bgcolor="#F0F2F6"><b>Attestation de prolongation expirée depuis le 11 octobre. <br>    Bonjour, <br>    Je vous sollicite pour le compte de l'un de 
nos adhérents, Monsieur C C, dont le numéro de la demande de renouvellement de carte de séjour est le 7500000000000000003. En effet, <span style='background-color: lightblue'>l'attestation de prolongation d'instruction de Monsieur
 C est arrivée à expiration depuis le 11 octobre 2024</span>. Aussi, il souhaiterait obtenir une nouvelle attestation pour pouvoir justifier de la régularité de son séjour, dans l'attente de recevoir carte de séjour. <br>    <br> 
   Sans action dans les prochains jours, <span style='background-color: pink'>il risquera de perdre son travail.</span><br>    <br>    Je vous remercie par avance et vous prie de noter l'urgence. <span style='background-color: pin
k'>Il risque son emploi, c'est donc très important.</span><br>    <br>    <br>    Ses coordonnées: <br>    Monsieur C C 78500 Sartrouville 07 00 00 00 00 CC@yahoo.com <br>    <br>    Bien à vous.</b></td></tr></table><br><span sty
le='background-color: lightblue'>Date d'expiration de l'API: 11/10/2024</span><br><span style='background-color: pink'>Mention de risque sur l'emploi: True</span><br><br><p style="font-weight: bold; color: blue;">3 - Notes</p>- L'API est expirée depuis 222 jours<br>- Risque sur l'emploi<br>
"""
    reponse_sauf_conduit = """En réponse à votre demande, je vous invite à nous adresser une copie des éléments suivants : 
    - l’acte de décès traduit 
    - votre acte de naissance 
    - la date des funérailles 
    - votre carte de séjour 
    - d'un justificatif de domicile de moins de 6 mois  en indiquant en objet URGENT DEMANDE DE SAUF CONDUIT. 

     En espérant vous avoir vous apporté les éléments souhaités,"""

    print("Sending email...")

    email_configuration = DistributionEmailConfiguration(
        locale="en",
        hub_email_address="envoishibou78@gmail.com",
        agent_email_address="pocagent78@gmail.com",
        case_field_email_address="",
        smtp_server="smtp.gmail.com",
        password="bceo rdxm suuv orul",
        smtp_port=587)

    email_to_send = Email(from_email_address="envoishibou78@gmail.com",
                          to_email_address="pocagent78@gmail.com",
                          subject="Subject",
                          body=body)

    email_mail_to = Email(from_email_address="pocagent78@gmail.com",
                          to_email_address="johndoe@outlook.com",
                          subject="Réponse à votre demande",
                          body=reponse_sauf_conduit)

    send_mail(email_configuration=email_configuration, email_to_send=email_to_send, email_mail_to=email_mail_to)
    print("Email sent!")


if __name__ == "__main__":
    main()
