from abc import ABC, abstractmethod
from typing import Literal, Any

from pydantic import BaseModel

from src.common.api import CaseHandlingRequest


class CaseHandlingDecisionInput(BaseModel):
    intention_id: str
    field_values: dict[str, Any]  # rename case field values


class CaseHandlingDecisionOutput(BaseModel):
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
    def decide(self, case_handling_decision_input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        pass
