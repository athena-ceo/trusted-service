import logging
from pathlib import Path
from typing import Any

from src.backend.backend.app import App
from src.common.case_model import CaseModel
from src.common.config import SupportedLocale
from src.common.server_api import CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.server_api import ServerApi


class TrustedServicesServer(ServerApi):

    def __init__(self, runtime_directory: str):
        logging.basicConfig(filename="log_file.log",
                            # level=logging.INFO,  # could be DEBUG, WARNING, ERROR
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            filemode='w')
        logger = logging.getLogger("TrustedServicesServer")
        logger.critical("TrustedServicesServer.__init__")
        print("TrustedServicesServer.__init__")

        self.runtime_directory = runtime_directory

        self.apps: dict[str, App] = {}  # To be ovedrriden in reload_apps
        self.reload_apps()

    def reload_apps(self):
        apps_subdirectory = Path(self.runtime_directory + "/apps")
        app_ids = [p.name for p in apps_subdirectory.iterdir() if p.is_dir()]

        self.apps: dict[str, App] = {
            app_id: App(self.runtime_directory, app_id, )
            for app_id in app_ids
        }

    def get_app_ids(self) -> list[str]:
        return list(self.apps.keys())

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        app: App = self.apps.get(app_id, None)
        if app is None:
            return []
        return app.get_locales(app_id)

    def get_llm_config_ids(self, app_id: str) -> list[str]:
        app: App = self.apps.get(app_id, None)
        if app is None:
            return []
        return app.get_llm_config_ids(app_id)

    def get_decision_engine_config_ids(self, app_id: str) -> list[str]:
        app: App = self.apps.get(app_id, None)
        if app is None:
            return []
        return app.get_decision_engine_config_ids(app_id)

    def get_app_name(self, app_id: str, locale: SupportedLocale) -> str:
        # TODO Catch exception
        return self.apps[app_id].get_app_name(app_id, locale)

    def get_app_description(self, app_id: str, locale: SupportedLocale) -> str:
        return self.apps[app_id].get_app_description(app_id, locale)

    def get_sample_message(self, app_id: str, locale: SupportedLocale) -> str:
        return self.apps[app_id].get_sample_message(app_id, locale)

    def get_case_model(self, app_id: str, locale: SupportedLocale) -> CaseModel:
        return self.apps[app_id].get_case_model(app_id, locale)

    def analyze(self, app_id: str, locale: SupportedLocale, field_values: dict[str, Any], text: str, read_from_cache: bool, llm_config_id: str) -> dict[str, Any]:
        result = self.apps[app_id].analyze(app_id, locale, field_values, text, read_from_cache, llm_config_id)
        return result

    def save_text_analysis_cache(self, app_id: str, locale: SupportedLocale, text_analysis_cache: str):
        self.apps[app_id].save_text_analysis_cache(app_id, locale, text_analysis_cache)

    def handle_case(self, app_id: str, locale: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        print(request.model_dump_json(indent=4))
        return self.apps[app_id].handle_case(app_id, locale, request)
