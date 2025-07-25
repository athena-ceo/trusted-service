from abc import ABC, abstractmethod

from src.backend.decision.decision import CaseHandlingDecisionOutput
from src.common.api import CaseHandlingRequest, CaseHandlingResponse
from src.common.case_model import CaseModel

class CaseHandlingDistributionEngine(ABC):  # TODO: pass App
    @abstractmethod
    def distribute(self,
                   case_model: CaseModel,
                   request: CaseHandlingRequest,
                   # case_handling_decision_output: CaseHandlingDecisionOutput) -> CaseHandlingResponse:
                   case_handling_decision_output: CaseHandlingDecisionOutput) -> tuple[str, str]:
        pass


