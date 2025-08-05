from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel

from src.common.case_model import CaseModel
from src.common.configuration import SupportedLocale


class CaseHandlingRequest(BaseModel):
    intention_id: str
    field_values: dict[str, Any]  # rename case field values
    highlighted_text_and_features: str


class CaseHandlingDecisionInput(BaseModel):
    intention_id: str
    field_values: dict[str, Any]  # rename case field values


class CaseHandlingDecisionOutput(BaseModel):
    handling: Literal["AUTOMATED", "AGENT", "DEFLECTION"]

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
    case_handling_report: tuple[str, str | None]  # 1rst element: Rendering of the mail to to the agent. 2nd element: Rendering of the mail to to the requester


class CaseHandlingDetailedResponse(BaseModel):
    case_handling_decision_input: CaseHandlingDecisionInput
    case_handling_decision_output: CaseHandlingDecisionOutput
    case_handling_response: CaseHandlingResponse


class Api(ABC):

    @abstractmethod
    def get_app_ids(self) -> list[str]:
        pass

    @abstractmethod
    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        pass

    @abstractmethod
    def get_app_name(self, app_id: str, loc: SupportedLocale) -> str:
        pass

    @abstractmethod
    def get_app_description(self, app_id: str, loc: SupportedLocale) -> str:
        pass

    @abstractmethod
    def get_sample_message(self, app_id: str, loc: SupportedLocale) -> str:
        pass

    @abstractmethod
    def get_case_model(self, app_id: str, loc: SupportedLocale) -> CaseModel:
        pass

    @abstractmethod
    def analyze(self, app_id: str, loc: SupportedLocale, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def handle_case(self, app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        pass
