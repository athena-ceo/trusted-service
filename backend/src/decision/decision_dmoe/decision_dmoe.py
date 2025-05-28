from backend.src.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecision
from backend.src.decision.decision_dmoe.decision_dmoe_configuration import DecisionDMOEConfiguration
from common.src.api import CaseHandlingRequest
from common.src.case_model import CaseModel


class CaseHandlingDecisionEngineDMOE(CaseHandlingDecisionEngine):
    def __init__(self, case_model: CaseModel, decision_dmoe_configuration: DecisionDMOEConfiguration):
        self.case_model: CaseModel = case_model
        self.dmoe_param: str = decision_dmoe_configuration.dmoe_param

    def decide(self, request: CaseHandlingRequest) -> CaseHandlingDecision:
        pass
