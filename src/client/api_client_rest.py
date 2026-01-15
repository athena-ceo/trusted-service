from __future__ import annotations

from typing import TYPE_CHECKING, Any

import requests

from src.client.api_client import ApiClient
from src.common.case_model import CaseModel
from src.common.constants import API_ROUTE_V2
from src.common.logging import print_red
from src.common.server_api import CaseHandlingDetailedResponse, CaseHandlingRequest

if TYPE_CHECKING:
    from src.common.config import SupportedLocale


class ApiClientRest(ApiClient):

    def __init__(self, http_connection_url: str) -> None:
        self.base_url = http_connection_url
        self._timeout = 10

    def get(
        self,
        suff: str,
        app_id: str | None = None,
        locale: SupportedLocale | None = None,
    ) -> any:

        url = f"{self.base_url}/{API_ROUTE_V2}"
        if app_id is not None:
            url += f"/apps/{app_id}"
            if locale is not None:
                url += f"/{locale}"
        url += f"/{suff}"
        response = requests.get(url, timeout=self._timeout)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def reload_apps(self):
        print_red("1")
        url = f"{self.base_url}/{API_ROUTE_V2}/reload_apps"
        response = requests.post(url, timeout=self._timeout)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_app_ids(self) -> list[str]:
        return self.get("app_ids")

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        return self.get("locales", app_id)

    def get_llm_config_ids(self, app_id: str) -> list[str]:
        return self.get("llm_config_ids", app_id)

    def get_decision_engine_config_ids(self, app_id: str) -> list[str]:
        return self.get("decision_engine_config_ids", app_id)

    def get_app_name(self, app_id: str, locale: SupportedLocale) -> str:
        return self.get("app_name", app_id, locale)

    def get_app_description(self, app_id: str, locale: SupportedLocale) -> str:
        return self.get("app_description", app_id, locale)

    def get_sample_message(self, app_id: str, locale: SupportedLocale) -> str:
        return self.get("sample_message", app_id, locale)

    def get_case_model(self, app_id: str, locale: SupportedLocale) -> CaseModel:
        case_model_data = self.get("case_model", app_id, locale)
        if case_model_data is None:
            return None
        return CaseModel.model_validate(case_model_data)

    def analyze(
        self,
        app_id: str,
        locale: SupportedLocale,
        field_values: dict[str, Any],
        text: str,
        read_from_cache: bool,
        llm_config_id: str,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{API_ROUTE_V2}/apps/{app_id}/{locale}/analyze"
        data = {
            "field_values": field_values,
            "text": text,
            "read_from_cache": read_from_cache,
            "llm_config_id": llm_config_id,
        }
        response = requests.post(url, json=data, timeout=self._timeout)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def save_text_analysis_cache(
        self,
        app_id: str,
        locale: SupportedLocale,
        text_analysis_cache: str,
    ):
        url = f"{self.base_url}/{API_ROUTE_V2}/apps/{app_id}/{locale}/save_text_analysis_cache"
        params = {"text_analysis_cache": text_analysis_cache}
        response = requests.post(url, params=params, timeout=self._timeout)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def handle_case(
        self,
        app_id: str,
        locale: SupportedLocale,
        request: CaseHandlingRequest,
    ) -> CaseHandlingDetailedResponse:
        url = f"{self.base_url}/{API_ROUTE_V2}/apps/{app_id}/{locale}/handle_case"
        response = requests.post(url, json=request.dict(), timeout=self._timeout)

        if response.status_code == 200:
            response_data = response.json()
            return CaseHandlingDetailedResponse.model_validate(response_data)
        else:
            return None
