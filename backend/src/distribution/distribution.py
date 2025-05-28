from abc import ABC, abstractmethod

from backend.src.decision.decision import CaseHandlingDecision
from common.src.api import CaseHandlingRequest, CaseHandlingResponse
from common.src.case_model import CaseModel

class CaseHandlingDistributionEngine(ABC):  # TODO: pass App
    @abstractmethod
    def distribute(self,
                   case_model: CaseModel,
                   request: CaseHandlingRequest,
                   case_handling_decision: CaseHandlingDecision) -> CaseHandlingResponse:
        pass


