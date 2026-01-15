from abc import ABC, abstractmethod

from src.common.server_api import CaseHandlingDecisionInput, CaseHandlingDecisionOutput


class CaseHandlingDecisionEngine(ABC):

    @abstractmethod
    def _decide(
        self,
        case_handling_decision_input: CaseHandlingDecisionInput,
    ) -> CaseHandlingDecisionOutput:
        pass

    def decide(
        self,
        case_handling_decision_input: CaseHandlingDecisionInput,
    ) -> CaseHandlingDecisionOutput:
        return self._decide(case_handling_decision_input)
