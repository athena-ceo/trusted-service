from abc import ABC
from typing import Any

import requests

from apps.delphes.design_time.src.app_delphes import AppDelphes
from src.backend.decision.decision import CaseHandlingDecisionInput, CaseHandlingDecisionOutput
from src.common.case_model import CaseModel
from src.common.api import Api, CaseHandlingRequest, CaseHandlingResponse, CaseHandlingDetailedResponse


class ApiClient(Api, ABC):
    pass


class ApiClientDirect(ApiClient):
    def __init__(self):
        self.api: Api = AppDelphes().api_implementation

    def get_case_model(self) -> CaseModel:
        return self.api.get_case_model()

    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        return self.api.analyze(field_values, text)

    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        return self.api.handle_case(request)


class ApiClientHttp(ApiClient):
    def __init__(self):
        self.base_url = "http://localhost:8002"

    def get_case_model(self) -> CaseModel:

        url = f"{self.base_url}/case_model"

        response = requests.get(url, params={})

        if response.status_code == 200:
            case_model_data = response.json()
            case_model = CaseModel.model_validate(case_model_data)
            return case_model
        else:
            print(f"Request failed with status code: {response.status_code}")

    def analyze(self, text: str) -> dict[str, Any]:
        url = f"{self.base_url}/analyze"
        response = requests.post(url, params={"text": text})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")

    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        url = f"{self.base_url}/process_request"
        response = requests.post(url, json=request.dict())

        if response.status_code == 200:
            response_data = response.json()
            response2 = CaseHandlingResponse.model_validate(response_data)
            return response2
        else:
            print(f"Request failed with status code: {response.status_code}")
