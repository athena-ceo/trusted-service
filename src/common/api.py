from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from src.common.case_model import CaseModel

class CaseHandlingRequest(BaseModel):
    intention_id: str
    field_values: dict[str, Any]  # rename case field values
    highlighted_text_and_features: str

class CaseHandlingResponse(BaseModel):
    acknowledgement_to_requester: str
    case_handling_report: str

class Api(ABC):

    @abstractmethod
    def get_case_model(self) -> CaseModel:
        pass

    # @abstractmethod
    # def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
    #     pass

    @abstractmethod
    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingResponse:
        pass
