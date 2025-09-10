import importlib
from typing import Any, cast

from pydantic import BaseModel

from src.backend.backend.localized_app import LocalizedApp
from src.backend.backend.paths import get_app_def_filename
from src.backend.backend.server_config import ServerConfig
from src.backend.decision.decision import CaseHandlingDecisionEngine
from src.backend.decision.decision_odm.decision_odm import CaseHandlingDecisionEngineODM
from src.backend.text_analysis.text_analyzer import LlmConfig
from src.common.server_api import CaseHandlingRequest, CaseHandlingDetailedResponse, CaseHandlingDecisionOutput, CaseHandlingDecisionInput, ServerApi
from src.common.case_model import CaseModel
from src.common.config import SupportedLocale, Config, load_config_from_workbook


class DecisionEngineConfig(BaseModel):
    id: str
    engine_type: str  # odm, python
    parameter1: str
    parameter2: str
    parameter3: str


class AppDef(Config):
    locales: str
    data_enrichment: str
    decision_engine_configs: list[DecisionEngineConfig]


def load_app_def_from_workbook(filename: str) -> AppDef:
    conf: Config = load_config_from_workbook(filename=filename,
                                             main_tab="app",
                                             collections=[  # ("llm_configs", LlmConfig),
                                                               ("decision_engine_configs", DecisionEngineConfig), ],
                                             config_type=AppDef,
                                             locale=None)

    return cast(AppDef, conf)


class App(ServerApi):

    def __init__(self, runtime_directory: str, app_id: str, ):
        self.runtime_directory = runtime_directory
        self.app_id: str = app_id

        server_config = ServerConfig.load_from_yaml_file(runtime_directory + "/config_server.yaml")
        self.llm_configs: dict[str, LlmConfig] = {llm_config.id: llm_config for llm_config in server_config.llm_configs}

        app_def_filename = get_app_def_filename(runtime_directory, app_id)
        app_def: AppDef = load_app_def_from_workbook(app_def_filename)

        self.locales: list[SupportedLocale] = [cast(SupportedLocale, locale.strip()) for locale in app_def.locales.split(',')]

        self.localized_apps: dict[str, LocalizedApp] = {
            locale: LocalizedApp(runtime_directory, app_id, self, locale)
            for locale in self.locales
        }

        self.data_enrichment = app_def.data_enrichment

        self.decision_engines: dict[str, CaseHandlingDecisionEngine] = {}
        for decision_engine_config in app_def.decision_engine_configs:
            if decision_engine_config.engine_type == "odm":

                decision_engine = CaseHandlingDecisionEngineODM(decision_service_url=decision_engine_config.parameter1,
                                                                trace_rules=decision_engine_config.parameter2 == "trace_rules")
            else:
                # module_name, sep, classname = app_def.decision_engine.rpartition(".")
                module_name, classname = decision_engine_config.parameter1, decision_engine_config.parameter2
                module = importlib.import_module(module_name)
                cls = getattr(module, classname)
                decision_engine = cls()
            self.decision_engines[decision_engine_config.id] = decision_engine

    def decide(self, decision_engine_config_id: str, case_handling_decision_input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        decision_engine = self.decision_engines[decision_engine_config_id]
        return decision_engine.decide(case_handling_decision_input)

    # API implementation

    def reload_apps(self):
        pass

    def get_app_ids(self) -> list[str]:
        pass

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        return self.locales

    def get_llm_config_ids(self, app_id: str) -> list[str]:
        llm_configs: dict[str, LlmConfig] = self.llm_configs
        return list(llm_configs.keys())

    def get_decision_engine_config_ids(self, app_id: str) -> list[str]:
        decision_engines: dict[str, CaseHandlingDecisionEngine] = self.decision_engines
        return list(decision_engines.keys())

    def get_app_name(self, app_id: str, locale: SupportedLocale) -> str:
        return self.localized_apps[locale].get_app_name(app_id, locale)

    def get_app_description(self, app_id: str, locale: SupportedLocale) -> str:
        return self.localized_apps[locale].get_app_description(app_id, locale)

    def get_sample_message(self, app_id: str, locale: SupportedLocale) -> str:
        return self.localized_apps[locale].get_sample_message(app_id, locale)

    def get_case_model(self, app_id: str, locale: SupportedLocale) -> CaseModel:
        return self.localized_apps[locale].get_case_model(app_id, locale)

    def analyze(self, app_id: str, locale: SupportedLocale, field_values: dict[str, Any], text: str, read_from_cache: bool, llm_config_id: str) -> dict[str, Any]:
        return self.localized_apps[locale].analyze(app_id, locale, field_values, text, read_from_cache, llm_config_id)

    def save_text_analysis_cache(self, app_id: str, locale: SupportedLocale, text_analysis_cache: str):
        return self.localized_apps[locale].save_text_analysis_cache(app_id, locale, text_analysis_cache)

    def handle_case(self, app_id: str, locale: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        return self.localized_apps[locale].handle_case(app_id, locale, request)
