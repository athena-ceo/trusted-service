from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput
from src.backend.decision.decision_dmoe.decision_drools_configuration import DecisionDroolsConfiguration
from src.common.case_model import CaseModel


class CaseHandlingDecisionEngineDrools(CaseHandlingDecisionEngine):
    def __init__(self, case_model: CaseModel, decision_drools_configuration: DecisionDroolsConfiguration):
        self.case_model: CaseModel = case_model
        self.drools_param: str = decision_drools_configuration.drools_param


    def decide(self, case_handling_decision_input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        pass
