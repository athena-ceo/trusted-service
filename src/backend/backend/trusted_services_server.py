from typing import Any

from src.backend.backend.app import App
from src.common.api import Api, CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.case_model import CaseModel
from src.common.configuration import SupportedLocale


class TrustedServicesServer(Api):

    def __init__(self, config_filenames: list[str]):
        self.apps: dict[str,App] = {}
        for config_filename in config_filenames:
            app = App(config_filename)
            self.apps[app.app_id] = app

    def get_app_ids(self) -> list[str]:
        return list(self.apps.keys())

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        app: App = self.apps.get(app_id, None)
        if app is None:
            return []
        return app.get_locales(app_id)

    def get_app_name(self, app_id: str, loc: SupportedLocale) -> str:
        # TODO Catch exception
        return self.apps[app_id].get_app_name(app_id, loc)

    def get_app_description(self, app_id: str, loc: SupportedLocale) -> str:
        return self.apps[app_id].get_app_description(app_id, loc)

    def get_sample_message(self, app_id: str, loc: SupportedLocale) -> str:
        return self.apps[app_id].get_sample_message(app_id, loc)

    def get_case_model(self, app_id: str, loc: SupportedLocale) -> CaseModel:
        return self.apps[app_id].get_case_model(app_id, loc)

    def analyze(self, app_id: str, loc: SupportedLocale, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        result = self.apps[app_id].analyze(app_id, loc, field_values, text)
        return result

    def handle_case(self, app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        return self.apps[app_id].handle_case(app_id, loc, request)
