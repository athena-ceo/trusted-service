import json

import requests
from pydantic import BaseModel, Field

from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput
from src.backend.decision.decision_odm.decision_odm_configuration import DecisionODMConfiguration
from src.common.case_model import CaseModel


class CaseHandlingDecisionEngineODM(CaseHandlingDecisionEngine):
    def __init__(self, case_model: CaseModel, decision_odm_configuration: DecisionODMConfiguration):
        self.case_model: CaseModel = case_model
        self.decision_service_url: str = decision_odm_configuration.decision_service_url
        self.trace_rules: bool = decision_odm_configuration.trace_rules

    def decide(self, case_handling_decision_input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:

        payload = {
            "intention": case_handling_decision_input.intention_id,
            "case_": case_handling_decision_input.field_values,
            "__TraceFilter__": {"infoRulesFired": self.trace_rules}
        }

        print("*********************")
        print(json.dumps(payload, indent=4))
        print("*********************")

        try:
            response = requests.post(self.decision_service_url, json=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
        except Exception as exception:
            error_msg = f"An error occurred: {exception}"
            print(error_msg)

        if response.status_code != 200:
            error_msg = f"Error: {response.status_code}\n{response.text}\n"
            print(error_msg)

        response_dict: dict = response.json()
        print(json.dumps(response_dict, indent=4))


        response_dict["decision"]["details"] = {
            "decision_id": response_dict["__DecisionID__"],
        }

        if self.trace_rules:
            traces: list[str] = []
            regles_executees = response_dict["__decisionTrace__"]["rulesFired"]["ruleInformation"]
            for regle_executee in regles_executees:
                business_name = regle_executee["businessName"]
                index = business_name.rfind('.')  # Position du dernier index
                id_dossier, id_regle = \
                    (business_name[:index], business_name[index + 1:]) if index != -1 else ("", business_name)
                print("id_dossier", id_dossier, "id_regle", id_regle)
                traces.append((id_dossier + "." + id_regle))
            response_dict["decision"]["details"]["traces"]= traces

        return CaseHandlingDecisionOutput(**response_dict["decision"])
