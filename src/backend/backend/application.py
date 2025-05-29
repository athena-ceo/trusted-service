# from apps.delphes.src.app_delphes import CaseHandlingDecisionEngineDelphesPython
import importlib

from src.backend.decision.decision import CaseHandlingDecisionEngine
from src.backend.decision.decision_odm.decision_odm import CaseHandlingDecisionEngineODM
from src.backend.decision.decision_odm.decision_odm_configuration import load_odm_configuration_from_workbook
from src.backend.distribution.distribution_email.distribution_email import CaseHandlingDistributionEngineEmail
from src.backend.distribution.distribution_email.distribution_email_configuration import DistributionEmailConfiguration, load_email_configuration_from_workbook
from src.backend.text_analysis.base_models import Feature
from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration, load_text_analysis_configuration_from_workbook
from src.backend.text_analysis.text_analyzer import TextAnalyzer
from src.common.case_model import load_case_model_configuration_from_workbook, CaseModelConfiguration, CaseModel
from src.backend.backend.api_implementation import ApiImplementation
from src.backend.backend.backend_configuration import BackendConfiguration, load_backend_configuration_from_workbook


class App:
    def __init__(self, configuration_filename: str, ):

        backend_configuration: BackendConfiguration = load_backend_configuration_from_workbook(configuration_filename)

        case_model_configuration: CaseModelConfiguration = load_case_model_configuration_from_workbook(configuration_filename)
        case_model: CaseModel = CaseModel(case_fields=case_model_configuration.case_fields)

        text_analysis_configuration: TextAnalysisConfiguration = load_text_analysis_configuration_from_workbook(configuration_filename)
        text_analyzer = TextAnalyzer(case_model,  text_analysis_configuration)

        if backend_configuration.decision_engine == "dmoe":
            pass
        elif backend_configuration.decision_engine == "odm":
            decision_odm_configuration = load_odm_configuration_from_workbook(configuration_filename)
            case_handling_decision_engine: CaseHandlingDecisionEngine = CaseHandlingDecisionEngineODM(case_model, decision_odm_configuration)
        else:
            # For instance "apps.delphes.src.app_delphes.CaseHandlingDecisionEngineDelphesPython"
            module_name, sep, classname = backend_configuration.decision_engine.rpartition(".")
            module = importlib.import_module(module_name)
            cls = getattr(module, classname)
            case_handling_decision_engine: CaseHandlingDecisionEngine = cls()

        if backend_configuration.distribution_engine == "email":
            email_configuration: DistributionEmailConfiguration = load_email_configuration_from_workbook(configuration_filename)
            case_handling_distribution_engine = CaseHandlingDistributionEngineEmail(email_configuration)
        else:  # Ticketong ssystem, etc...
            pass

        self.api_implementation = ApiImplementation(case_model,
                                                    text_analyzer,
                                                    case_handling_decision_engine,
                                                    case_handling_distribution_engine)
