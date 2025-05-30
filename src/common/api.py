from abc import ABC, abstractmethod
from typing import Any, Literal, Optional

from pydantic import BaseModel

from src.common.case_model import CaseModel


class CaseHandlingRequest(BaseModel):
    intention_id: str
    field_values: dict[str, Any]  # rename case field values
    highlighted_text_and_features: str


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

    # Free-format traces, anything that can be displayed
    # For instance, with ODM, it will contain __DecisionID__ and optionally __decisionTrace__
    details: Any = None


class CaseHandlingResponse(BaseModel):
    acknowledgement_to_requester: str
    case_handling_report: str


class CaseHandlingDetailedResponse(BaseModel):
    case_handling_decision_input: CaseHandlingDecisionInput
    case_handling_decision_output: CaseHandlingDecisionOutput
    case_handling_response: CaseHandlingResponse


class Api(ABC):

    @abstractmethod
    def get_case_model(self) -> CaseModel:
        pass

    @abstractmethod
    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        pass
