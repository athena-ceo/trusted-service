from __future__ import annotations

import requests

from src.backend.decision.decision import (
    CaseHandlingDecisionEngine,
    CaseHandlingDecisionInput,
    CaseHandlingDecisionOutput,
)


class CaseHandlingDecisionEngineODM(CaseHandlingDecisionEngine):

    def __init__(self, decision_service_url: str, trace_rules: bool) -> None:

        self.decision_service_url: str = decision_service_url
        self.trace_rules: bool = trace_rules

    def _decide(
        self,
        case_handling_decision_input: CaseHandlingDecisionInput,
    ) -> CaseHandlingDecisionOutput:

        payload = {
            "intention": case_handling_decision_input.intention_id,
            "case_": case_handling_decision_input.field_values,
            "__TraceFilter__": {"infoRulesFired": self.trace_rules},
        }

        try:
            response = requests.post(
                self.decision_service_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
        except Exception:
            pass

        if response.status_code != 200:
            pass

        response_dict: dict = response.json()

        response_dict["decision"]["details"] = {
            "decision_id": response_dict["__DecisionID__"],
        }

        if self.trace_rules:
            traces: list[str] = []
            regles_executees = response_dict["__decisionTrace__"]["rulesFired"][
                "ruleInformation"
            ]
            for regle_executee in regles_executees:
                business_name = regle_executee["businessName"]
                index = business_name.rfind(".")  # Position du dernier index
                id_dossier, id_regle = (
                    (business_name[:index], business_name[index + 1 :])
                    if index != -1
                    else ("", business_name)
                )
                traces.append(id_dossier + "." + id_regle)
            response_dict["decision"]["details"]["traces"] = traces

        return CaseHandlingDecisionOutput(**response_dict["decision"])
