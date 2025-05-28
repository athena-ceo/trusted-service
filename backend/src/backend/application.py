# from apps.delphes.src.app_delphes import CaseHandlingDecisionEngineDelphesPython
import importlib

from backend.src.backend.api_implementation import ApiImplementation
from backend.src.backend.backend_configuration import load_backend_configuration_from_workbook, BackendConfiguration
from backend.src.decision.decision import CaseHandlingDecisionEngine
from backend.src.decision.decision_odm.decision_odm import CaseHandlingDecisionEngineODM
from backend.src.decision.decision_odm.decision_odm_configuration import load_odm_configuration_from_workbook
from backend.src.distribution.distribution_email.distribution_email import CaseHandlingDistributionEngineEmail
from backend.src.distribution.distribution_email.distribution_email_configuration import DistributionEmailConfiguration, load_email_configuration_from_workbook
from backend.src.text_analysis.base_models import Feature
from backend.src.text_analysis.text_analysis_configuration import TextAnalysisConfiguration, load_text_analysis_configuration_from_workbook
from backend.src.text_analysis.text_analyzer import TextAnalyzer
from common.src.case_model import load_case_model_from_workbook, CaseModel


class App:
    def __init__(self, configuration_filename: str, ):

        backend_configuration: BackendConfiguration = load_backend_configuration_from_workbook(configuration_filename)

        case_model: CaseModel = load_case_model_from_workbook(configuration_filename)

        text_analysis_configuration: TextAnalysisConfiguration = load_text_analysis_configuration_from_workbook(configuration_filename)
        features = []
        for case_field in case_model.case_fields: ## TODO: Do that in the constructor of TextAnalyzer
            if case_field.extraction != "DO NOT EXTRACT":
                feature = Feature(id=case_field.id,
                                  label=case_field.label,
                                  type=case_field.get_type(),
                                  description=case_field.description,
                                  highlight_fragments=case_field.extraction == "EXTRACT AND HIGHLIGHT")
                features.append(feature)
        text_analyzer = TextAnalyzer(text_analysis_configuration, features)

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
