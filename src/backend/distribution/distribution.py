from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.backend.decision.decision import CaseHandlingDecisionOutput
    from src.common.case_model import CaseModel
    from src.common.server_api import CaseHandlingRequest


class CaseHandlingDistributionEngine(ABC):  # TODO: pass App
    @abstractmethod
    def distribute(
        self,
        case_model: CaseModel,
        request: CaseHandlingRequest,
        intent_label: str,
        case_handling_decision_output: CaseHandlingDecisionOutput,
    ) -> tuple[str, str]:
        pass
