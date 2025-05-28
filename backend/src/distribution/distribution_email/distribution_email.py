from typing import Optional

from backend.src.backend.api_implementation import CaseHandlingDistributionEngine, CaseHandlingDecision
from backend.src.distribution.distribution_email.email2 import Email
from backend.src.distribution.distribution_email.distribution_email_configuration import DistributionEmailConfiguration, ResponseTemplate
from backend.src.distribution.distribution_email.send_email import send_mail
from backend.src.rendering.html import render_email, hilite_blue
from common.src.api import CaseHandlingRequest, CaseHandlingResponse
from common.src.case_model import CaseModel


class CaseHandlingDistributionEngineEmail(CaseHandlingDistributionEngine):

    def __init__(self, email_configuration: DistributionEmailConfiguration):
        self.email_configuration = email_configuration

    @staticmethod
    def _build_email_body(case_model: CaseModel,
                          request: CaseHandlingRequest,
                          case_handling_decision: CaseHandlingDecision) -> str:

        body = "<br>" + hilite_blue("1 - Données du cas")
        body += "<b>Intention</b>: " + request.intention_id + "<br>"

        # Show the field labels and values

        for case_field_id, case_field_value in request.field_values.items():
            case_field = case_model.get_field_by_id(case_field_id)
            case_field_label = case_field.label
            body += f"<b>{case_field_label}</b>: {str(case_field_value)}<br>"

        # Show the highlighted text and features

        body += "<br>" + hilite_blue("2 - Demande rédigée par le demandeur")
        body += request.highlighted_text_and_features
        body += "<br>"

        # Show the notes

        if notes := case_handling_decision.notes:
            body += "<br>" + hilite_blue("3 - Notes")
            for note in notes:
                body += f"- {note}<br>"

        return body

    def distribute(self,
                   case_model: CaseModel,
                   request: CaseHandlingRequest,
                   case_handling_decision: CaseHandlingDecision) -> CaseHandlingResponse:

        template_body: str = self._build_email_body(case_model, request, case_handling_decision, )

        print("BODY", template_body)

        email_to_send: Email = Email(
            from_email_address=self.email_configuration.hub_email_address,
            to_email_address=self.email_configuration.agent_email_address,
            subject=f"{case_handling_decision.work_basket} - {case_handling_decision.priority}",
            body=template_body)

        if case_handling_decision.treatment == "DEFLECTION":
            processing_report = "<h3>Réorientation du demandeur</h3><br>"
        else:
            processing_report = "<h3>Envoi d'un mail pour traitement par un agent</h3><br>"

        processing_report += "<h4>Email envoyé à l'agent</h4>"
        processing_report += render_email(email_to_send)

        email_mail_to: Optional[Email] = None

        if case_handling_decision.response_template_id:

            template: Optional[ResponseTemplate] = None
            for template2 in self.email_configuration.email_templates:
                template2: ResponseTemplate
                if template2.id == case_handling_decision.response_template_id:
                    template = template2
                    break

            if template is None:
                raise Exception(f"Email template {case_handling_decision.response_template_id} not found")

            template_body = template.body

            for k, v in request.field_values.items():
                template_body = template_body.replace("{" + k + "}", str(v))

            email_mail_to = Email(
                from_email_address=self.email_configuration.agent_email_address,
                to_email_address=request.field_values[self.email_configuration.case_field_email_address],
                subject=template.subject,
                body=template_body
            )

            processing_report += "<h4>Proposition de réponse au demandeur</h4>"
            processing_report += render_email(email_mail_to)

        print(email_to_send, email_mail_to)

        send_mail(email_configuration=self.email_configuration, email_to_send=email_to_send, email_mail_to=email_mail_to)

        print("b")

        return CaseHandlingResponse(acknowledgement_to_requester=case_handling_decision.acknowledgement_to_requester,
                                    case_handling_report=processing_report)
