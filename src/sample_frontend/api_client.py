import json
from abc import ABC
from typing import Any

import requests

from src.backend.backend.application import Application
from src.common.case_model import CaseModel
from src.common.api import Api, CaseHandlingRequest, CaseHandlingDetailedResponse


class ApiClient(Api, ABC):
    pass


class ApiClientDirect(ApiClient):
    def __init__(self, config_filename: str):
        self.api: Api = Application(config_filename).api_implementation

    def get_case_model(self) -> CaseModel:
        return self.api.get_case_model()

    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        return self.api.analyze(field_values, text)

    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        return self.api.handle_case(request)


class ApiClientHttp(ApiClient):
    def __init__(self, http_connection_url: str):
        self.base_url = http_connection_url

    def get_case_model(self) -> CaseModel:

        url = f"{self.base_url}/case_model"

        response = requests.get(url, params={})

        if response.status_code == 200:
            case_model_data = response.json()
            case_model = CaseModel.model_validate(case_model_data)
            return case_model
        else:
            print(f"Request failed with status code: {response.status_code}")

    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        url = f"{self.base_url}/analyze"
        response = requests.post(url, params={"field_values": json.dumps(field_values), "text": text})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")

    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        url = f"{self.base_url}/process_request"
        response = requests.post(url, json=request.dict())

        if response.status_code == 200:
            response_data = response.json()
            response2 = CaseHandlingDetailedResponse.model_validate(response_data)
            return response2
        else:
            print(f"Request failed with status code: {response.status_code}")
