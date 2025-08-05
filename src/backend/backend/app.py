from typing import Any, cast

from pydantic import Field

from src.backend.backend.localized_app import LocalizedApp
from src.common.api import CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.case_model import CaseModel
from src.common.configuration import SupportedLocale, Configuration, load_configuration_from_workbook
from src.common.logging import print_red


class AppConfiguration(Configuration):
    app_id: str
    runtime_directory: str  # The directory where various app-specific runtime artefacts are stored, in particular the caching of text analysis.
    locales: str
    # supported_locales: list[str] = Field(default_factory=list)  # TODO SupportedLocale
    # It is relative to the directory from where the app is run


def load_app_configuration_from_workbook(filename: str) -> AppConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="app",
                                                           collections=[],
                                                           configuration_type=AppConfiguration,
                                                           locale=None)

    return cast(AppConfiguration, conf)


class App:

    def __init__(self, config_filename: str):
        # common_configuration: CommonConfiguration = load_common_configuration_from_workbook(config_filename)
        # locale: SupportedLocale = common_configuration.locale
        app_configuration: AppConfiguration = load_app_configuration_from_workbook(config_filename)

        # app_id: str = app_configuration.app_id
        # app_name: str = app_configuration.app_name
        # app_description: str = app_configuration.app_description

        # messages_to_agent: list[Message] = app_configuration.messages_to_agent
        # messages_to_requester: list[Message] = app_configuration.messages_to_requester

        # case_model_configuration: CaseModelConfiguration = load_case_model_configuration_from_workbook(config_filename, locale)
        # case_model: CaseModel = CaseModel(case_fields=case_model_configuration.case_fields)

        # text_analysis_configuration: TextAnalysisConfiguration = load_text_analysis_configuration_from_workbook(config_filename, locale)
        # text_analyzer = TextAnalyzer(case_model, app_configuration.runtime_directory, text_analysis_configuration, locale)

        # if app_configuration.decision_engine == "odm":
        #     decision_odm_configuration = load_odm_configuration_from_workbook(config_filename, locale)
        #     case_handling_decision_engine = CaseHandlingDecisionEngineODM(case_model, decision_odm_configuration)
        # else:
        #     # For instance "apps.delphes.src.app_delphes.CaseHandlingDecisionEngineDelphesPython"
        #     module_name, sep, classname = app_configuration.decision_engine.rpartition(".")
        #     module = importlib.import_module(module_name)
        #     cls = getattr(module, classname)
        #     case_handling_decision_engine = cls()
        #
        # case_handling_distribution_engine: CaseHandlingDistributionEngine = None
        # if app_configuration.distribution_engine == "email":
        #     email_configuration: DistributionEmailConfiguration = load_email_configuration_from_workbook(config_filename, locale)
        #     case_handling_distribution_engine = CaseHandlingDistributionEngineEmail(email_configuration, locale)
        # else:  # Ticketing ssystem, etc...
        #     pass

        self.app_id: str = app_configuration.app_id
        self.runtime_directory: str = app_configuration.runtime_directory
        # self.app_name = app_name
        # self.app_description = app_description
        # self.messages_to_agent = messages_to_agent
        # self.messages_to_requester = messages_to_requester
        # self.case_model: CaseModel = case_model
        # self.text_analyzer: TextAnalyzer = text_analyzer
        # self.case_handling_decision_engine: CaseHandlingDecisionEngine = case_handling_decision_engine
        # self.case_handling_distribution_engine: CaseHandlingDistributionEngine = case_handling_distribution_engine

        self.locales: list[SupportedLocale] = [cast(SupportedLocale, loc.strip()) for loc in app_configuration.locales.split(',')]

        print_red("locales", )

        self.localized_apps: dict[str, LocalizedApp] = {}
        for locale in self.locales:
            localized_app = LocalizedApp(config_filename, self, locale)
            self.localized_apps[locale] = localized_app

    def get_app_ids(self) -> list[str]:
        pass

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        return self.locales

    def get_app_name(self, app_id: str, loc: SupportedLocale) -> str:
        return self.localized_apps[loc].get_app_name(app_id, loc)

    def get_app_description(self, app_id: str, loc: SupportedLocale) -> str:
        return self.localized_apps[loc].get_app_description(app_id, loc)

    def get_sample_message(self, app_id: str, loc: SupportedLocale) -> str:
        return self.localized_apps[loc].get_sample_message(app_id, loc)

    def get_case_model(self, app_id: str, loc: SupportedLocale) -> CaseModel:
        return self.localized_apps[loc].get_case_model(app_id, loc)

    def analyze(self, app_id: str, loc: SupportedLocale, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        return self.localized_apps[loc].analyze(app_id, loc, field_values, text)

    # @staticmethod
    # def verbalize(list_verbalized_messages: list[Message], message_to_verbalize: str):
    #     # if s starts with a "#" and is the key of a registered message to requester, then replace it with its text
    #     if message_to_verbalize.startswith("#"):
    #         words = [word.strip() for word in message_to_verbalize[1:].split(",")]
    #         if words:
    #             key = words[0]
    #             if key:
    #                 # Look for key in configuration
    #                 if m := [m for m in list_verbalized_messages if m.key == key]:
    #                     format_string = m[0].text  # A string that potentially contains {0}, {1}, {2}, etc
    #                     values = words[1:]
    #                     return format_string.format(*values)
    #     return message_to_verbalize
    #

    def handle_case(self, app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
        return self.localized_apps[loc].handle_case(app_id, loc, request)

    # def handle_case(self, app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
    #
    #     # Filter-out the field values that are not to be sent to the decision engine
    #     field_values: dict[str, Any] = {}
    #     for case_field in self.case_model.case_fields:
    #         if case_field.send_to_decision_engine:
    #             field_values[case_field.id] = request.field_values[case_field.id]
    #
    #     case_handling_decision_input = CaseHandlingDecisionInput(intention_id=request.intention_id, field_values=field_values)
    #
    #     case_handling_decision_output: CaseHandlingDecisionOutput = self.case_handling_decision_engine.decide(case_handling_decision_input)
    #
    #     # A verbalized copy of case_handling_decision_output
    #     verbalized_case_handling_decision_output = case_handling_decision_output.copy(deep=True)
    #     notes = verbalized_case_handling_decision_output.notes
    #     verbalized_case_handling_decision_output.notes = [self.verbalize(self.messages_to_agent, note) for note in notes]
    #     verbalized_case_handling_decision_output.acknowledgement_to_requester = self.verbalize(self.messages_to_requester,
    #                                                                                            verbalized_case_handling_decision_output.acknowledgement_to_requester)
    #
    #     intent_label = None
    #     for intent in self.text_analyzer.config2.intentions:
    #         if intent.id == request.intention_id:
    #             intent_label = intent.label
    #
    #     rendering_email_to_agent, rendering_email_to_requester = self.case_handling_distribution_engine.distribute(
    #         self.case_model,  # TODO avoid passing this
    #         request,
    #         intent_label,
    #         verbalized_case_handling_decision_output)
    #
    #     case_handling_response: CaseHandlingResponse = CaseHandlingResponse(
    #         acknowledgement_to_requester=verbalized_case_handling_decision_output.acknowledgement_to_requester,
    #         case_handling_report=(rendering_email_to_agent, rendering_email_to_requester)
    #     )
    #
    #     return CaseHandlingDetailedResponse(case_handling_decision_input=case_handling_decision_input,
    #                                         case_handling_decision_output=case_handling_decision_output,
    #                                         case_handling_response=case_handling_response)
