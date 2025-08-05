import json
from abc import ABC, ABCMeta
from typing import Any

import requests

from src.backend.backend.trusted_services_server import TrustedServicesServer
from src.common.case_model import CaseModel
from src.common.api import Api, CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.configuration import SupportedLocale
from src.common.constants import API_ROUTE_V2


class ApiClient(Api, ABC):
    pass


class ApiClientDirect(ApiClient):
    def __init__(self, config_filenames: list[str]):
        self.api: Api = TrustedServicesServer(config_filenames)

    def get_app_ids(self) -> list[str]:
        return self.api.get_app_ids()

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        return self.api.get_locales(app_id)

    def get_app_name(self, app_id: str, loc: SupportedLocale) -> str:
        return self.api.get_app_name(app_id, loc)

    def get_app_description(self, app_id: str, loc: SupportedLocale) -> str:
        return self.api.get_app_description(app_id, loc)

    def get_sample_message(self, app_id: str, loc: SupportedLocale) -> str:
        return self.api.get_sample_message(app_id, loc)

    def get_case_model(self, app_id: str, loc: SupportedLocale) -> CaseModel:
        case_model: CaseModel = self.api.get_case_model(app_id, loc)
        return case_model

    def analyze(self, app_id: str, loc: SupportedLocale, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        return self.api.analyze(app_id, loc, field_values, text)

    def handle_case(self, app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        return self.api.handle_case(app_id, loc, request)


class ApiClientHttp(ApiClient):

    def __init__(self, http_connection_url: str):
        self.base_url = http_connection_url

    def get(self, suff: str, app_id: str | None = None, locale: str | None = None, ) -> any:

        url = f"{self.base_url}/{API_ROUTE_V2}"
        if app_id is not None:
            url += f"/apps/{app_id}"
            if locale is not None:
                url += f"/{locale}"
        url += f"/{suff}"
        print("url", url)
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")

    def get_app_ids(self) -> list[str]:
        return self.get("app_ids")

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        return self.get("locales", app_id)

    def get_app_name(self, app_id: str, loc: SupportedLocale) -> str:
        return self.get("app_name", app_id, loc)

    def get_app_description(self, app_id: str, loc: SupportedLocale) -> str:
        return self.get("app_description", app_id, loc)

    def get_sample_message(self, app_id: str, loc: SupportedLocale) -> str:
        return self.get("sample_message", app_id, loc)

    def get_case_model(self, app_id: str, loc: SupportedLocale) -> CaseModel:
        case_model_data = self.get("case_model", app_id, loc)
        if case_model_data is None:
            return None
        return CaseModel.model_validate(case_model_data)

    def analyze(self, app_id: str, loc: SupportedLocale, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        url = f"{self.base_url}/{API_ROUTE_V2}/apps/{app_id}/{loc}/analyze"
        response = requests.post(url, params={"field_values": json.dumps(field_values), "text": text})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")

    def handle_case(self, app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        url = f"{self.base_url}/{API_ROUTE_V2}/apps/{app_id}/{loc}/handle_case"
        response = requests.post(url, json=request.dict())

        if response.status_code == 200:
            response_data = response.json()
            response2 = CaseHandlingDetailedResponse.model_validate(response_data)
            return response2
        else:
            print(f"Request failed with status code: {response.status_code}")
