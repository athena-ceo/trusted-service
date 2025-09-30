import importlib
import json
from typing import Any, cast

from pydantic import BaseModel, ValidationError

from src.backend.backend.paths import get_cache_file_path, get_app_def_filename
from src.backend.distribution.distribution import CaseHandlingDistributionEngine
from src.backend.distribution.distribution_email.distribution_email import CaseHandlingDistributionEngineEmail
from src.backend.distribution.distribution_email.distribution_email_config import DistributionEmailConfig, load_email_config_from_workbook
from src.backend.text_analysis.llm import LlmConfig
from src.backend.text_analysis.text_analyzer import TextAnalyzer, TextAnalysisConfig, load_text_analysis_config_from_workbook
from src.common.logging import print_red, print_blue
from src.common.server_api import ServerApi, CaseHandlingRequest, CaseHandlingResponse, CaseHandlingDetailedResponse, CaseHandlingDecisionInput, CaseHandlingDecisionOutput
from src.common.case_model import CaseModel, CaseModelConfig, load_case_model_config_from_workbook
from src.common.config import SupportedLocale, Config, load_config_from_workbook


class Message(BaseModel):
    key: str
    text: str


class LocalizedAppConfig(Config):
    app_name: str
    app_description: str
    sample_message: str
    distribution_engine: str
    messages_to_agent: list[Message]
    messages_to_requester: list[Message]


def load_localized_app_config_from_workbook(filename: str, locale: SupportedLocale) -> LocalizedAppConfig:
    conf: Config = load_config_from_workbook(filename=filename,
                                             main_tab="localized_app",
                                             collections=[("messages_to_agent", Message),
                                                          ("messages_to_requester", Message)],
                                             config_type=LocalizedAppConfig,
                                             locale=locale)

    return cast(LocalizedAppConfig, conf)


class LocalizedApp(ServerApi):

    def __init__(self, runtime_directory: str, app_id: str, parent_app: 'App', locale: SupportedLocale):

        self.runtime_directory: str = runtime_directory
        self.app_id: str = app_id
        self.parent_app: 'App' = parent_app
        self.locale: SupportedLocale = locale

        # READ FROM localized_app_config

        app_def_filename = get_app_def_filename(runtime_directory, app_id)
        localized_app_config = load_localized_app_config_from_workbook(app_def_filename, locale)

        self.app_name: str = localized_app_config.app_name
        self.app_description: str = localized_app_config.app_description
        self.sample_message: str = localized_app_config.sample_message

        self.case_handling_distribution_engine: CaseHandlingDistributionEngine | None = None
        if localized_app_config.distribution_engine == "email":
            email_config: DistributionEmailConfig = load_email_config_from_workbook(app_def_filename, locale)
            
            # Clean any problematic characters from config to avoid ASCII encoding errors
            def clean_string(s):
                if isinstance(s, str):
                    # Replace non-breaking space and other problematic characters
                    return s.replace('\xa0', ' ').replace('\u00a0', ' ')
                return s
            
            # Clean all string fields in config
            email_config.hub_email_address = clean_string(email_config.hub_email_address)
            email_config.agent_email_address = clean_string(email_config.agent_email_address)
            email_config.password = clean_string(email_config.password)
            email_config.smtp_server = clean_string(email_config.smtp_server)
            
            self.case_handling_distribution_engine = CaseHandlingDistributionEngineEmail(email_config, locale)
        else:  # Ticketing system, etc...
            pass

        self.messages_to_agent: list[Message] = localized_app_config.messages_to_agent
        self.messages_to_requester: list[Message] = localized_app_config.messages_to_requester

        #####

        case_model_config: CaseModelConfig = load_case_model_config_from_workbook(app_def_filename, locale)
        case_model: CaseModel = CaseModel(case_fields=case_model_config.case_fields)
        self.case_model: CaseModel = case_model

        self.text_analysis_config: TextAnalysisConfig = load_text_analysis_config_from_workbook(app_def_filename, locale)
        self.text_analyzer = TextAnalyzer(runtime_directory, app_id, locale, case_model, self.text_analysis_config)

    # API implementation

    def reload_apps(self):
        pass

    def get_app_ids(self) -> list[str]:
        pass

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        pass

    def get_llm_config_ids(self, app_id: str) -> list[str]:
        pass

    def get_decision_engine_config_ids(self, app_id: str) -> list[str]:
        pass

    def get_app_name(self, app_id: str, locale: SupportedLocale) -> str:
        return self.app_name

    def get_app_description(self, app_id: str, locale: SupportedLocale) -> str:
        return self.app_description

    def get_sample_message(self, app_id: str, locale: SupportedLocale) -> str:
        return self.sample_message

    def get_case_model(self, app_id: str, locale: SupportedLocale) -> CaseModel:
        return self.case_model

    def analyze(self, app_id: str, locale: SupportedLocale, field_values: dict[str, Any], text: str, read_from_cache: bool, llm_config_id: str) -> dict[str, Any]:

        llm_configs: dict[str, LlmConfig] = self.parent_app.llm_configs
        llm_config: LlmConfig = llm_configs[llm_config_id]
        result = self.text_analyzer.analyze(llm_config, field_values, text, read_from_cache)
        return result

    def save_text_analysis_cache(self, app_id: str, locale: SupportedLocale, text_analysis_cache: str):
        print_blue("SAVING")
        print_blue(text_analysis_cache)
        text_analysis_cache_dict = json.loads(text_analysis_cache)
        print_blue()
        hash_code = text_analysis_cache_dict["hash_code"]
        cache_filename = get_cache_file_path(self.runtime_directory, self.app_id, self.locale, hash_code)
        with open(file=cache_filename, mode="w", encoding="utf-8") as f:
            f.write(text_analysis_cache)

    @staticmethod
    def verbalize(list_verbalized_messages: list[Message], message_to_verbalize: str):
        # if s starts with a "#" and is the key of a registered message to requester, then replace it with its text
        if message_to_verbalize.startswith("#"):
            words = [word.strip() for word in message_to_verbalize[1:].split(",")]
            if words:
                key = words[0]
                if key:
                    # Look for key in config
                    if m := [m for m in list_verbalized_messages if m.key == key]:
                        format_string = m[0].text  # A string that potentially contains {0}, {1}, {2}, etc
                        values = words[1:]
                        return format_string.format(*values)
        return message_to_verbalize

    def handle_case(self, app_id: str, locale: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:

        # Data enrichment
        if self.parent_app.data_enrichment:
            module_name, function_name = self.parent_app.data_enrichment.rsplit(".", 1)
            module = importlib.import_module(module_name)
            func = getattr(module, function_name)
            func(request.field_values)

        # Filter-out the field values that are not to be sent to the decision engine
        field_values: dict[str, Any] = {}
        for case_field in self.case_model.case_fields:
            if case_field.send_to_decision_engine:
                field_values[case_field.id] = request.field_values[case_field.id]

        case_handling_decision_input = CaseHandlingDecisionInput(intention_id=request.intention_id, field_values=field_values)

        case_handling_decision_output: CaseHandlingDecisionOutput = self.parent_app.decide(request.decision_engine_config_id, case_handling_decision_input)

        try:
            CaseHandlingDecisionOutput.model_validate(case_handling_decision_output)
        except ValidationError as exc:
            print_red("ValidationError", repr(exc.errors()[0]['type']))
            print_red(exc.json(indent=4))
            print_blue(case_handling_decision_output)
            print_blue(case_handling_decision_output.handling)
            print_blue(case_handling_decision_output.acknowledgement_to_requester)
            print_blue(case_handling_decision_output.response_template_id)
            print_blue(case_handling_decision_output.work_basket)
            print_blue(case_handling_decision_output.priority)
            print_blue(case_handling_decision_output.notes)
            print_blue(case_handling_decision_output.details)
            print(str(exc))
            input("-> ")
        else:
            print_red("no ValidationError")

        # A verbalized copy of case_handling_decision_output
        verbalized_case_handling_decision_output = case_handling_decision_output.copy(deep=True)
        notes = verbalized_case_handling_decision_output.notes
        verbalized_case_handling_decision_output.notes = [self.verbalize(self.messages_to_agent, note) for note in notes]
        verbalized_case_handling_decision_output.acknowledgement_to_requester = self.verbalize(self.messages_to_requester,
                                                                                               verbalized_case_handling_decision_output.acknowledgement_to_requester)

        intent_label = None

        for intent in self.text_analysis_config.intentions:
            if intent.id == request.intention_id:
                intent_label = intent.label

        rendering_email_to_agent, rendering_email_to_requester = self.case_handling_distribution_engine.distribute(
            self.case_model,  # TODO avoid passing this
            request,
            intent_label,
            verbalized_case_handling_decision_output)

        case_handling_response: CaseHandlingResponse = CaseHandlingResponse(
            acknowledgement_to_requester=verbalized_case_handling_decision_output.acknowledgement_to_requester,
            case_handling_report=(rendering_email_to_agent, rendering_email_to_requester)
        )

        print_red(type(case_handling_decision_output), case_handling_decision_output)

        return CaseHandlingDetailedResponse(case_handling_decision_input=case_handling_decision_input,
                                            case_handling_decision_output=case_handling_decision_output,
                                            case_handling_response=case_handling_response)
