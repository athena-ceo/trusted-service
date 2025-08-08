import importlib
from typing import Any, cast

from pydantic import BaseModel

from src.backend.backend.localized_app import LocalizedApp
from src.backend.decision.decision import CaseHandlingDecisionEngine
from src.backend.decision.decision_odm.decision_odm import CaseHandlingDecisionEngineODM
from src.common.api import CaseHandlingRequest, CaseHandlingDetailedResponse, CaseHandlingDecisionOutput, CaseHandlingDecisionInput, Api
from src.common.case_model import CaseModel
from src.common.configuration import SupportedLocale, Configuration, load_configuration_from_workbook


class DecisionEngineConfig(BaseModel):
    id: str
    label: str
    engine_type: str  # odm, python
    parameter1: str
    parameter2: str
    parameter3: str


class LlmConfig(BaseModel):
    id: str
    label: str
    llm: str
    model: str
    response_format_type: str
    prompt_format: str
    temperature: str


class AppConfiguration(Configuration):
    app_id: str
    runtime_directory: str  # The directory where various app-specific runtime artefacts are stored, in particular the caching of text analysis.
    locales: str
    llm_configs: list[LlmConfig]
    decision_engine_configs: list[DecisionEngineConfig]


def load_app_configuration_from_workbook(filename: str) -> AppConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="app",
                                                           collections=[("llm_configs", LlmConfig),
                                                                        ("decision_engine_configs", DecisionEngineConfig)],
                                                           configuration_type=AppConfiguration,
                                                           locale=None)

    return cast(AppConfiguration, conf)


class App(Api):

    def __init__(self, config_filename: str):
        app_configuration: AppConfiguration = load_app_configuration_from_workbook(config_filename)

        self.app_id: str = app_configuration.app_id
        self.runtime_directory: str = app_configuration.runtime_directory

        self.locales: list[SupportedLocale] = [cast(SupportedLocale, loc.strip()) for loc in app_configuration.locales.split(',')]

        self.localized_apps: dict[str, LocalizedApp] = {}
        for locale in self.locales:
            localized_app = LocalizedApp(config_filename, self, locale)
            self.localized_apps[locale] = localized_app

        self.llm_configs: dict[str, LlmConfig] = {llm_config.id: llm_config for llm_config in app_configuration.llm_configs}

        self.decision_engines: dict[str, CaseHandlingDecisionEngine] = {}
        for decision_engine_config in app_configuration.decision_engine_configs:
            if decision_engine_config.engine_type == "odm":

                decision_engine = CaseHandlingDecisionEngineODM(decision_service_url=decision_engine_config.parameter1,
                                                                trace_rules=decision_engine_config.parameter2 == "trace")
            else:
                # module_name, sep, classname = app_configuration.decision_engine.rpartition(".")
                module_name, classname = decision_engine_config.parameter1, decision_engine_config.parameter2
                module = importlib.import_module(module_name)
                cls = getattr(module, classname)
                decision_engine = cls()
            self.decision_engines[decision_engine_config.id] = decision_engine

    def decide(self, decision_engine_config_id: str, case_handling_decision_input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        # return self.case_handling_decision_engine.decide(case_handling_decision_input)
        decision_engine = self.decision_engines[decision_engine_config_id]
        return decision_engine.decide(case_handling_decision_input)

    # API implementation

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

    def get_app_name(self, app_id: str, loc: SupportedLocale) -> str:
        return self.localized_apps[loc].get_app_name(app_id, loc)

    def get_app_description(self, app_id: str, loc: SupportedLocale) -> str:
        return self.localized_apps[loc].get_app_description(app_id, loc)

    def get_sample_message(self, app_id: str, loc: SupportedLocale) -> str:
        return self.localized_apps[loc].get_sample_message(app_id, loc)

    def get_case_model(self, app_id: str, loc: SupportedLocale) -> CaseModel:
        return self.localized_apps[loc].get_case_model(app_id, loc)

    def analyze(self, app_id: str, loc: SupportedLocale, field_values: dict[str, Any], text: str, read_from_cache: bool) -> dict[str, Any]:
        return self.localized_apps[loc].analyze(app_id, loc, field_values, text, read_from_cache)

    def save_text_analysis_cache(self, app_id: str, loc: str, text_analysis_cache: str):
        return self.localized_apps[loc].save_text_analysis_cache(app_id, loc, text_analysis_cache)

    def handle_case(self, app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        return self.localized_apps[loc].handle_case(app_id, loc, request)
