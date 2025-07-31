import importlib
from typing import Any

from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook

from src.backend.decision.decision_odm.decision_odm import CaseHandlingDecisionEngineODM
from src.backend.decision.decision_odm.decision_odm_configuration import load_odm_configuration_from_workbook
from src.backend.distribution.distribution import CaseHandlingDistributionEngine
from src.backend.distribution.distribution_email.distribution_email import CaseHandlingDistributionEngineEmail
from src.backend.distribution.distribution_email.distribution_email_configuration import DistributionEmailConfiguration, load_email_configuration_from_workbook
from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration, load_text_analysis_configuration_from_workbook
from src.backend.text_analysis.text_analyzer import TextAnalyzer
from src.common.case_model import load_case_model_configuration_from_workbook, CaseModelConfiguration, CaseModel, OptionalListElement
from src.backend.backend.api_implementation import ApiImplementation
from src.backend.backend.backend_configuration import BackendConfiguration, load_backend_configuration_from_workbook, Message
from src.common.common_configuration import load_common_configuration_from_workbook, CommonConfiguration
from src.common.configuration import SupportedLocale, load_pydantic_objects_from_worksheet


class Application:
    def __init__(self, config_filename: str, ):

        common_configuration: CommonConfiguration = load_common_configuration_from_workbook(config_filename)
        locale: SupportedLocale = common_configuration.locale
        backend_configuration: BackendConfiguration = load_backend_configuration_from_workbook(config_filename, locale)

        app_name: str = backend_configuration.app_name
        app_description: str = backend_configuration.app_description

        messages_to_agent: list[Message] = backend_configuration.messages_to_agent
        messages_to_requester: list[Message] = backend_configuration.messages_to_requester

        # TODO delete
        # option_configuration: IdLabelsConfiguration = load_id_labels_configuration_from_workbook(config_filename, locale)

        case_model_configuration: CaseModelConfiguration = load_case_model_configuration_from_workbook(config_filename, locale)
        case_model: CaseModel = CaseModel(case_fields=case_model_configuration.case_fields)

        # dict2: dict[str, OptionalListElement] = {option.id: option for option in option_configuration.id_labels}

        # TODO Move that logic to CaseModelConfiguration
        for case_field in case_model.case_fields:

            if case_field.allowed_values_list_name:

                config_workbook: Workbook = load_workbook(config_filename)
                worksheet = config_workbook[case_field.allowed_values_list_name]
                case_field.allowed_values = load_pydantic_objects_from_worksheet(worksheet, OptionalListElement, locale)

        text_analysis_configuration: TextAnalysisConfiguration = load_text_analysis_configuration_from_workbook(config_filename, locale)
        text_analyzer = TextAnalyzer(case_model, backend_configuration.runtime_directory, text_analysis_configuration, locale)

        if backend_configuration.decision_engine == "odm":
            decision_odm_configuration = load_odm_configuration_from_workbook(config_filename, locale)
            case_handling_decision_engine = CaseHandlingDecisionEngineODM(case_model, decision_odm_configuration)
        else:
            # For instance "apps.delphes.src.app_delphes.CaseHandlingDecisionEngineDelphesPython"
            module_name, sep, classname = backend_configuration.decision_engine.rpartition(".")
            module = importlib.import_module(module_name)
            cls = getattr(module, classname)
            case_handling_decision_engine = cls()

        case_handling_distribution_engine: CaseHandlingDistributionEngine = None
        if backend_configuration.distribution_engine == "email":
            email_configuration: DistributionEmailConfiguration = load_email_configuration_from_workbook(config_filename, locale)
            case_handling_distribution_engine = CaseHandlingDistributionEngineEmail(email_configuration, locale)
        else:  # Ticketing ssystem, etc...
            pass

        self.api_implementation = ApiImplementation(app_name,
                                                    app_description,
                                                    messages_to_agent,
                                                    messages_to_requester,
                                                    case_model,
                                                    text_analyzer,
                                                    case_handling_decision_engine,
                                                    case_handling_distribution_engine)
