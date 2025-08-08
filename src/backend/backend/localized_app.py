import importlib
from typing import Any, cast

from pydantic import BaseModel

from src.backend.distribution.distribution import CaseHandlingDistributionEngine
from src.backend.distribution.distribution_email.distribution_email import CaseHandlingDistributionEngineEmail
from src.backend.distribution.distribution_email.distribution_email_configuration import DistributionEmailConfiguration, load_email_configuration_from_workbook
from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration, load_text_analysis_configuration_from_workbook
from src.backend.text_analysis.text_analyzer import TextAnalyzer
from src.common.api import Api, CaseHandlingRequest, CaseHandlingResponse, CaseHandlingDetailedResponse, CaseHandlingDecisionInput, CaseHandlingDecisionOutput
from src.common.case_model import CaseModel, CaseModelConfiguration, load_case_model_configuration_from_workbook
from src.common.configuration import SupportedLocale, Configuration, load_configuration_from_workbook


class Message(BaseModel):
    key: str
    text: str

class LocalizedAppConfiguration(Configuration):
    app_name: str
    app_description: str
    sample_message: str
    # decision_engine: str
    distribution_engine: str
    messages_to_agent: list[Message]
    messages_to_requester: list[Message]


def load_localized_app_configuration_from_workbook(filename: str, locale: SupportedLocale) -> LocalizedAppConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="localized_app",
                                                           collections=[("messages_to_agent", Message),
                                                                        ("messages_to_requester", Message)],
                                                           configuration_type=LocalizedAppConfiguration,
                                                           locale=locale)

    return cast(LocalizedAppConfiguration, conf)


class LocalizedApp(Api):

    def __init__(self, config_filename: str, parent_app: 'App', locale: SupportedLocale, ):

        localized_app_configuration = load_localized_app_configuration_from_workbook(config_filename, locale)

        self.parent_app: 'App' = parent_app
        self.locale = locale

        app_name: str = localized_app_configuration.app_name
        app_description: str = localized_app_configuration.app_description
        sample_message: str = localized_app_configuration.sample_message
        messages_to_agent: list[Message] = localized_app_configuration.messages_to_agent
        messages_to_requester: list[Message] = localized_app_configuration.messages_to_requester

        case_model_configuration: CaseModelConfiguration = load_case_model_configuration_from_workbook(config_filename, locale)
        case_model: CaseModel = CaseModel(case_fields=case_model_configuration.case_fields)
        self.case_model: CaseModel = case_model

        text_analysis_configuration: TextAnalysisConfiguration = load_text_analysis_configuration_from_workbook(config_filename, locale)
        text_analyzer = TextAnalyzer(self, text_analysis_configuration)

        case_handling_distribution_engine: CaseHandlingDistributionEngine = None
        if localized_app_configuration.distribution_engine == "email":
            email_configuration: DistributionEmailConfiguration = load_email_configuration_from_workbook(config_filename, locale)
            case_handling_distribution_engine = CaseHandlingDistributionEngineEmail(email_configuration, locale)
        else:  # Ticketing system, etc...
            pass

        # self.app_id = app_id
        self.app_name = app_name
        self.app_description = app_description
        self.sample_message = sample_message
        self.messages_to_agent = messages_to_agent
        self.messages_to_requester = messages_to_requester
        self.text_analyzer: TextAnalyzer = text_analyzer
        # self.case_handling_decision_engine: CaseHandlingDecisionEngine = case_handling_decision_engine
        self.case_handling_distribution_engine: CaseHandlingDistributionEngine = case_handling_distribution_engine

    def get_app_ids(self) -> list[str]:
        pass

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        pass

    def get_llm_config_ids(self, app_id: str) -> list[str]:
        pass

    def get_decision_engine_config_ids(self, app_id: str) -> list[str]:
        pass

    def get_app_name(self, app_id: str, loc: SupportedLocale) -> str:
        return self.app_name

    def get_app_description(self, app_id: str, loc: SupportedLocale) -> str:
        return self.app_description

    def get_sample_message(self, app_id: str, loc: SupportedLocale) -> str:
        return self.sample_message

    def get_case_model(self, app_id: str, loc: SupportedLocale) -> CaseModel:
        return self.case_model

    def analyze(self, app_id: str, loc: SupportedLocale, field_values: dict[str, Any], text: str, read_from_cache: bool) -> dict[str, Any]:
        result = self.text_analyzer.analyze(field_values, text, read_from_cache)
        return result

    def save_text_analysis_cache(self, app_id: str, loc: str, text_analysis_cache: str):
        cache_filename = ("{directory}/cache_{app_id}_{locale}.json".
                          format(directory=self.parent_app.runtime_directory,
                                 app_id=self.parent_app.app_id,
                                 locale=self.locale))
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
                    # Look for key in configuration
                    if m := [m for m in list_verbalized_messages if m.key == key]:
                        format_string = m[0].text  # A string that potentially contains {0}, {1}, {2}, etc
                        values = words[1:]
                        return format_string.format(*values)
        return message_to_verbalize

    def handle_case(self, app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:

        # Filter-out the field values that are not to be sent to the decision engine
        field_values: dict[str, Any] = {}
        for case_field in self.case_model.case_fields:
            if case_field.send_to_decision_engine:
                field_values[case_field.id] = request.field_values[case_field.id]

        case_handling_decision_input = CaseHandlingDecisionInput(intention_id=request.intention_id, field_values=field_values)

        case_handling_decision_output: CaseHandlingDecisionOutput = self.parent_app.decide(request.decision_engine_config_id, case_handling_decision_input)

        # A verbalized copy of case_handling_decision_output
        verbalized_case_handling_decision_output = case_handling_decision_output.copy(deep=True)
        notes = verbalized_case_handling_decision_output.notes
        verbalized_case_handling_decision_output.notes = [self.verbalize(self.messages_to_agent, note) for note in notes]
        verbalized_case_handling_decision_output.acknowledgement_to_requester = self.verbalize(self.messages_to_requester,
                                                                                               verbalized_case_handling_decision_output.acknowledgement_to_requester)

        intent_label = None
        for intent in self.text_analyzer.config2.intentions:
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

        return CaseHandlingDetailedResponse(case_handling_decision_input=case_handling_decision_input,
                                            case_handling_decision_output=case_handling_decision_output,
                                            case_handling_response=case_handling_response)
