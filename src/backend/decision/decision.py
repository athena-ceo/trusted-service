from abc import ABC, abstractmethod

from src.common.api import CaseHandlingDecisionInput, CaseHandlingDecisionOutput


class CaseHandlingDecisionEngine(ABC):
    @abstractmethod
    def decide(self, case_handling_decision_input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        pass
