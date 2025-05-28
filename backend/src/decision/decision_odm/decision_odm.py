import json
from typing import Literal, Any

import requests

from backend.src.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecision
from backend.src.decision.decision_odm.decision_odm_configuration import DecisionODMConfiguration
from common.src.api import CaseHandlingRequest
from common.src.case_model import CaseModel


class CaseHandlingDecisionEngineODM(CaseHandlingDecisionEngine):
    def __init__(self, case_model: CaseModel, decision_odm_configuration: DecisionODMConfiguration):
        self.case_model: CaseModel = case_model
        self.decision_service_url: str = decision_odm_configuration.decision_service_url

    def decide(self, request: CaseHandlingRequest) -> CaseHandlingDecision:

        field_values: dict[str, Any] = {}

        for case_field in self.case_model.case_fields:
            if case_field.send_to_decision_engine:
                field_values[case_field.id] = request.field_values[case_field.id]

        payload = {
            "intention": request.intention_id,
            "case_": field_values,
            # "__TraceFilter__": {
            #     "infoRulesFired": True
            # }
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

        return CaseHandlingDecision(**response_dict["decision"])
