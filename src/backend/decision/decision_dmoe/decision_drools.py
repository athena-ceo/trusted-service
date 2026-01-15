from src.backend.decision.decision import (
    CaseHandlingDecisionEngine,
    CaseHandlingDecisionInput,
    CaseHandlingDecisionOutput,
)
from src.backend.decision.decision_dmoe.decision_drools_config import (
    DecisionDroolsConfig,
)
from src.common.case_model import CaseModel


class CaseHandlingDecisionEngineDrools(CaseHandlingDecisionEngine):
    def __init__(
        self,
        case_model: CaseModel,
        decision_drools_config: DecisionDroolsConfig,
    ) -> None:
        self.case_model: CaseModel = case_model
        self.drools_param: str = decision_drools_config.drools_param

    def _decide(
        self,
        case_handling_decision_input: CaseHandlingDecisionInput,
    ) -> CaseHandlingDecisionOutput:
        pass
