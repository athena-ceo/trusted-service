from typing import Optional

from src.backend.decision.decision import CaseHandlingDecisionOutput
from src.backend.distribution.distribution import CaseHandlingDistributionEngine
from src.backend.distribution.distribution_email.distribution_email_configuration import EmailTemplate
from src.backend.distribution.distribution_email.distribution_email_localization import distribution_engine_email_localizations
from src.backend.rendering.html import render_email, hilite_blue, standard_table_style
from src.common.api import CaseHandlingRequest, CaseHandlingResponse
from src.common.case_model import CaseModel

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

from src.backend.distribution.distribution_email.email2 import Email
from src.backend.distribution.distribution_email.distribution_email_configuration import DistributionEmailConfiguration
from src.common.configuration import SupportedLocale


class CaseHandlingDistributionEngineEmail(CaseHandlingDistributionEngine):

    def __init__(self, email_configuration: DistributionEmailConfiguration, locale: SupportedLocale):
        self.email_configuration = email_configuration
        self.locale: SupportedLocale = locale
        self.localization = distribution_engine_email_localizations[locale]  # Will fail here if language is not supported

    def build_body_of_email_to_agent(self,
                                     case_model: CaseModel,
                                     request: CaseHandlingRequest,
                                     case_handling_decision_output: CaseHandlingDecisionOutput) -> str:

        # Build table with field values

        labels_and_values = [(self.localization.label_intent, request.intention_id)]
        for case_field_id, case_field_value in request.field_values.items():
            case_field = case_model.get_field_by_id(case_field_id)
            case_field_label = case_field.label

            case_field_value2 = case_field_value
            if isinstance(case_field_value, bool):
                case_field_value2 = self.localization.label_yes if case_field_value else self.localization.label_no

            labels_and_values.append((case_field_label, case_field_value2))

        table = "<table cellpadding='10'>\n"
        for label, value in labels_and_values:
            table += f"<tr><td bgcolor=#F0F2F6>{label}</td><td>{value}</td></tr>\n"
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
                   # case_handling_decision_output: CaseHandlingDecisionOutput) -> CaseHandlingResponse:
                   case_handling_decision_output: CaseHandlingDecisionOutput) -> tuple[str, str]:

        # email_to_agent

        body_of_email_to_agent: str = self.build_body_of_email_to_agent(case_model, request, case_handling_decision_output, )

        email_to_agent: Email = Email(
            from_email_address=self.email_configuration.hub_email_address,
            to_email_address=self.email_configuration.agent_email_address,
            subject=f"{case_handling_decision_output.work_basket} - {case_handling_decision_output.priority}",
            body=body_of_email_to_agent)

        # email_to_requester

        email_to_requester: Optional[Email] = None

        template_id: str = case_handling_decision_output.response_template_id
        if template_id:  # if a template is defined
            matching_templates = [template for template in self.email_configuration.email_templates if template.id == template_id]
            if matching_templates:
                template: EmailTemplate = matching_templates[0]
                body_of_email_to_requester = template.body
                for k, v in request.field_values.items():
                    body_of_email_to_requester = body_of_email_to_requester.replace("{" + k + "}", str(v))
                email_to_requester = Email(
                    from_email_address=self.email_configuration.agent_email_address,
                    to_email_address=request.field_values[self.email_configuration.case_field_email_address],
                    subject=template.subject,
                    body=body_of_email_to_requester
                )

        # Send emails

        if self.email_configuration.send_email:
            print("SENDING EMAIL")
            self.send_mail(email_configuration=self.email_configuration, email_to_send=email_to_agent, email_mail_to=email_to_requester)
        else:
            print("NOT SENDING EMAIL")

        # Return response to client

        rendering_email_to_agent = render_email(email_to_agent)
        rendering_email_to_requester = render_email(email_to_requester)  # is None if email_to_requester is None

        # return CaseHandlingResponse(acknowledgement_to_requester=case_handling_decision_output.acknowledgement_to_requester,
                                    # case_handling_report=(rendering_email_to_agent, rendering_email_to_requester))

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
            mailto_link = self.create_mailto_link(
                email=email_mail_to.to_email_address,
                subject=email_mail_to.subject,
                body=email_mail_to.body,
            )
            body += "<br>Répondre à " + mailto_link

        body += "</blockquote> </html>"

        return body

    def send_mail(self,
                  email_configuration: DistributionEmailConfiguration,
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

        body = self.build_body(body=email_to_send.body, email_mail_to=email_mail_to)

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
            print("Successfully sent email!")
        except Exception as e:
            print(f"Did not successfully send email!: {e}")
