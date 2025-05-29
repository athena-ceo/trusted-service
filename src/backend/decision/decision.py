from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel

from src.common.api import CaseHandlingRequest


class CaseHandlingDecision(BaseModel):
    treatment: Literal["AUTOMATED", "AGENT", "DEFLECTION"]

    # Decisions related to the communication with the requester
    acknowledgement_to_requester: str
    response_template_id: str

    # Decisions related to the work allocation
    work_basket: str
    priority: Literal["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
    notes: list[str]


class CaseHandlingDecisionEngine(ABC):
    @abstractmethod
    def decide(self, request: CaseHandlingRequest) -> CaseHandlingDecision:
        pass
