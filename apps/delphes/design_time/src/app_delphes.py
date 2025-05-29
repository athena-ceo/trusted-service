from datetime import datetime
from typing import Literal

from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecision
from src.common.api import CaseHandlingRequest
from src.backend.backend.application import App


class CaseHandlingDecisionEngineDelphesPython(CaseHandlingDecisionEngine):
    def decide(self, request: CaseHandlingRequest) -> CaseHandlingDecision:

        treatment: Literal["AUTOMATED", "AGENT", "DEFLECTION"]

        # Decisions related to the communication with the requester
        acknowledgement_to_requester: str
        response_template: str

        # Decisions related to the work allocation
        work_basket: str
        priority: Literal["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
        notes: list[str] = []

        if request.intention_id == "expiration_d_une_api":
            treatment = "AGENT"
            acknowledgement_to_requester = "Nous vous répondrons dans les meilleurs délais à propos de l'expiration de votre API"
            response_template = "expiration_d_une_api"
            work_basket = "api_a_renouveler"
            priority = "VERY_HIGH" if request.field_values["mention_de_risque_sur_l_emploi"] else "HIGH"

            date_demande = request.field_values["date_demande"]
            date_expiration_api = request.field_values["date_expiration_api"]
            date_format = "%d/%m/%Y"
            date_demande = datetime.strptime(date_demande, date_format)
            date_expiration_api = datetime.strptime(date_expiration_api, date_format)
            difference_in_days = (date_expiration_api - date_demande).days
            if difference_in_days < 0:
                notes.append(f"L'API est expirée depuis {-difference_in_days} jours")
            else:
                notes.append(f"L'API expire dans {difference_in_days} jours")

            if request.field_values["mention_de_risque_sur_l_emploi"]:
                notes.append("Risque sur l'emploi")

        else:
            treatment = "DEFLECTION"
            acknowledgement_to_requester = "Veuillez aller sur le site de l'OFPRA"
            response_template = ""
            work_basket = "réorientation"
            priority = "VERY_LOW"

        # subject = f"AGDREF - {work_basket} - {priority}"

        return CaseHandlingDecision(
            treatment=treatment,
            acknowledgement_to_requester=acknowledgement_to_requester,
            response_template_id=response_template,
            work_basket=work_basket,
            priority=priority,
            notes=notes,
        )


class AppDelphes(App):
    def __init__(self):
        super().__init__(configuration_filename="apps/delphes/runtime/configuration_delphes.xlsx")
