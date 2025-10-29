from typing import List, Optional
import logging

from src.backend.decision.decision import CaseHandlingDecisionOutput
from src.backend.distribution.distribution import CaseHandlingDistributionEngine
from src.backend.distribution.distribution_email.distribution_email_config import EmailTemplate, load_email_config_from_workbook
from src.backend.distribution.distribution_email.distribution_email_localization import distribution_engine_email_localizations
from src.backend.rendering.html import render_email, hilite_blue, standard_table_style, standard_back_ground_color
from src.common.server_api import CaseHandlingRequest, CaseHandlingResponse
from src.common.case_model import CaseModel

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

from src.backend.distribution.distribution_email.email2 import Email
from src.backend.distribution.distribution_email.distribution_email_config import DistributionEmailConfig
from src.common.config import SupportedLocale


class CaseHandlingDistributionEngineEmail(CaseHandlingDistributionEngine):

    def __init__(self, email_config: DistributionEmailConfig, locale: SupportedLocale):
        self.email_config = email_config
        self.locale: SupportedLocale = locale
        self.localization = distribution_engine_email_localizations[locale]  # Will fail here if language is not supported

    def build_body_of_email_to_agent(self,
                                     case_model: CaseModel,
                                     request: CaseHandlingRequest,
                                     intent_label: str,
                                     case_handling_decision_output: CaseHandlingDecisionOutput) -> str:

        # Build table with field values

        labels_and_values = [(self.localization.label_intent, intent_label)]
        for case_field_id, case_field_value in request.field_values.items():
            try:
                case_field = case_model.get_field_by_id(case_field_id)
                case_field_label = case_field.label
            except ValueError:
                # Defensive: if the case model does not define this field id,
                # don't crash the whole request. Log a warning and use the
                # field id as a fallback label so the email still contains the
                # provided value.
                logging.getLogger(__name__).warning(
                    "Field id '%s' not found in case model; including raw value in email.", case_field_id
                )
                case_field_label = case_field_id

            case_field_value2 = case_field_value
            if isinstance(case_field_value, bool):
                case_field_value2 = self.localization.label_yes if case_field_value else self.localization.label_no

            labels_and_values.append((case_field_label, case_field_value2))

        table = "<table cellpadding='10'>\n"
        for label, value in labels_and_values:
            table += f"<tr><td bgcolor={standard_back_ground_color}>{label}</td><td>{value}</td></tr>\n"
        table += "</table>"

        body = standard_table_style + table + "<br>"

        # Show the highlighted text and features

        body += request.highlighted_text_and_features
        body += "<br>"

        # Show the Alerts

        if notes := case_handling_decision_output.notes:
            table = "<table cellpadding='10'>\n"
            table += f"<tr><th>{self.localization.label_notes}</th></tr>\n"
            for note in notes:
                table += f"<tr><td>{note}</td></tr>\n"
            table += "</table>"
            body += table + "<br>"

        return body

    def distribute(self,
                   case_model: CaseModel,
                   request: CaseHandlingRequest,
                   intent_label: str,
                   # case_handling_decision_output: CaseHandlingDecisionOutput) -> CaseHandlingResponse:
                   case_handling_decision_output: CaseHandlingDecisionOutput) -> tuple[str, str]:

        # email_to_agent

        body_of_email_to_agent: str = self.build_body_of_email_to_agent(case_model, request, intent_label, case_handling_decision_output, )

        email_to_agent: Email = Email(
            from_email_address=self.email_config.hub_email_address,
            to_email_address=self.email_config.agent_email_address,
            subject=f"{case_handling_decision_output.work_basket} - {case_handling_decision_output.priority}",
            body=body_of_email_to_agent)

        # email_to_requester

        email_to_requester: Optional[Email] = None

        template_id: str = case_handling_decision_output.response_template_id
        if template_id:  # if a template is defined
            matching_templates = [template for template in self.email_config.email_templates if template.id == template_id]
            if matching_templates:
                template: EmailTemplate = matching_templates[0]
                body_of_email_to_requester = template.body
                # for k, v in request.field_values.items():
                #     body_of_email_to_requester = body_of_email_to_requester.replace("{" + k + "}", str(v))
                # More elegant:

                body_of_email_to_requester = body_of_email_to_requester.format(**request.field_values)

                email_to_requester = Email(
                    from_email_address=self.email_config.agent_email_address,
                    to_email_address=request.field_values[self.email_config.case_field_email_address],
                    subject=template.subject,
                    body=body_of_email_to_requester
                )

        # Send emails

        if self.email_config.send_email:
            print("SENDING EMAIL")
            self.send_mail(email_config=self.email_config, email_to_send=email_to_agent, email_mail_to=email_to_requester)
        else:
            print("NOT SENDING EMAIL")

        # Return response to client

        rendering_email_to_agent = render_email(email_to_agent)
        rendering_email_to_requester = render_email(email_to_requester)  # is None if email_to_requester is None

        return rendering_email_to_agent, rendering_email_to_requester

    @staticmethod
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

    def build_body(self, body: str, email_mail_to: Optional[Email]) -> str:
        body = "<html> <blockquote>" + body

        if email_mail_to is not None:
            # Ensure email is a string (take the first if it's a list)
            to_email = email_mail_to.to_email_address
            if isinstance(to_email, list):
                to_email = to_email[0] if to_email else ""
            mailto_link = self.create_mailto_link(
                email=to_email,
                subject=email_mail_to.subject,
                body=email_mail_to.body,
            )
            body += "<br>mailto" + mailto_link

        body += "</blockquote> </html>"

        return body

    def send_mail(self,
                  email_config: DistributionEmailConfig,
                  email_to_send: Email,
                  email_mail_to: Optional[Email]) -> None:
        email_password = email_config.password
        smtp_server = email_config.smtp_server
        smtp_port = email_config.smtp_port

        # Build MIME message
        message = MIMEMultipart()
        message["From"] = email_to_send.from_email_address

        # Normalize To header (accept str or list)
        if isinstance(email_to_send.to_email_address, list):
            message["To"] = ", ".join(email_to_send.to_email_address)
        else:
            message["To"] = email_to_send.to_email_address

        # Subject
        subject = email_to_send.subject
        if isinstance(subject, str):
            subject = subject.encode('utf-8').decode('utf-8')
        message["Subject"] = subject

        # Prepare body (HTML) using UTF-8
        body = self.build_body(body=email_to_send.body, email_mail_to=email_mail_to)
        # Ensure body is properly encoded
        if isinstance(body, str):
            body = body.encode('utf-8').decode('utf-8')
        message.attach(MIMEText(body, "html", "utf-8"))

        # Accept either `bcc` (new) or `bcc_email_address` (legacy) on Email model
        bcc_list: List[str] | None = getattr(email_to_send, "bcc", None) or getattr(email_to_send, "bcc_email_address", None)

        try:
            from email.utils import getaddresses

            # Build recipients for SMTP envelope: include To and Bcc
            address_strings: list[str] = []
            if isinstance(email_to_send.to_email_address, list):
                address_strings.extend(email_to_send.to_email_address)
            else:
                address_strings.append(email_to_send.to_email_address)

            if bcc_list:
                address_strings.extend(bcc_list)

            parsed = getaddresses(address_strings)
            recipients: List[str] = [addr for name, addr in parsed if addr]

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                # Disable SMTP protocol debug output in production
                server.set_debuglevel(0)
                server.starttls()
                server.login(email_to_send.from_email_address, email_password)

                # Send as bytes to preserve UTF-8
                server.sendmail(email_to_send.from_email_address, recipients, message.as_bytes())

            print("Successfully sent email!")
        except Exception as e:
            print(f"Did not successfully send email!: {e}")



# Ajout d'une fonction main pour tests unitaires d'envoi d'email
if __name__ == "__main__":
    import os

    locale = "fr"
    email_config: DistributionEmailConfig = load_email_config_from_workbook(
        os.path.join(os.path.dirname(__file__), "../../../../runtime/apps/delphes/delphes.xlsx"),
        locale)
    
    # Clean any problematic characters from config
    def clean_string(s):
        if isinstance(s, str):
            # Replace non-breaking space and other problematic characters
            return s.replace('\xa0', ' ').replace('\u00a0', ' ')
        return s
    
    # Clean all string fields in config
    email_config.hub_email_address = clean_string(email_config.hub_email_address)
    print(f"email_config.hub_email_address: {email_config.hub_email_address}")
    email_config.agent_email_address = clean_string(email_config.agent_email_address)
    print(f"email_config.agent_email_address: {email_config.agent_email_address}")
    email_config.password = clean_string(email_config.password)
    print(f"email_config.password: {email_config.password}")
    email_config.smtp_server = clean_string(email_config.smtp_server)
    print(f"email_config.smtp_server: {email_config.smtp_server}")
    
    # Override agent email for testing
    email_config.agent_email_address = "j@milgram.fr"
    engine = CaseHandlingDistributionEngineEmail(email_config, locale)

    email_to_agent: Email = Email(
        from_email_address=email_config.hub_email_address,
        to_email_address=email_config.agent_email_address,
        bcc_email_address=["Joel Milgram <joel@athenadecisions.com>", "joel@milgram.fr"],
        subject="Test d'email",
        body="Ceci est un test d'email envoye par le moteur de distribution.")

    engine.send_mail(email_config=email_config, email_to_send=email_to_agent, email_mail_to=None)
