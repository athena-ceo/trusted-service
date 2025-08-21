from datetime import datetime
from typing import Literal

from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput


class CaseHandlingDecisionEngineDelphesPython_OLD(CaseHandlingDecisionEngine):
    def _decide(self, case_handling_decision_input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:

        handling: Literal["AUTOMATED", "AGENT", "DEFLECTION"]

        # Decisions related to the communication with the requester
        acknowledgement_to_requester: str
        response_template: str

        # Decisions related to the work allocation
        work_basket: str
        priority: Literal["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        notes: list[str] = []

        if case_handling_decision_input.intention_id == "expiration_d_une_api":
            handling = "AGENT"
            acknowledgement_to_requester = "Nous vous répondrons dans les meilleurs délais à propos de l'expiration de votre API"
            response_template = "api-a-renouveler"
            work_basket = "api-a-renouveler"
            priority = "VERY_HIGH" if case_handling_decision_input.field_values["mention_de_risque_sur_l_emploi"] else "HIGH"

            # notes
            date_demande = case_handling_decision_input.field_values["date_demande"]
            date_expiration_api = case_handling_decision_input.field_values["date_expiration_api"]
            date_format = "%d/%m/%Y"
            date_demande = datetime.strptime(date_demande, date_format)
            date_expiration_api = datetime.strptime(date_expiration_api, date_format)
            difference_in_days = (date_expiration_api - date_demande).days
            if difference_in_days < 0:
                notes.append(f"L'API est expirée depuis {-difference_in_days} jours")
            else:
                notes.append(f"L'API expire dans {difference_in_days} jours")

            if case_handling_decision_input.field_values["mention_de_risque_sur_l_emploi"]:
                notes.append("Risque sur l'emploi")

        else:
            handling = "DEFLECTION"
            acknowledgement_to_requester = "Veuillez aller sur le site de l'OFPRA"
            response_template = ""
            work_basket = "reorientation"
            priority = "VERY_LOW"

        return CaseHandlingDecisionOutput(
            handling=handling,
            acknowledgement_to_requester=acknowledgement_to_requester,
            response_template_id=response_template,
            work_basket=work_basket,
            priority=priority,
            notes=notes,
            details="The hardcoded implementation does not provide traceability information yet"
        )
