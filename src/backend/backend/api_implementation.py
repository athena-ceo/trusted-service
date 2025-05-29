from typing import Any

from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecision
from src.backend.distribution.distribution import CaseHandlingDistributionEngine
from src.backend.text_analysis.text_analyzer import TextAnalyzer
from src.common.api import Api, CaseHandlingRequest, CaseHandlingResponse
from src.common.case_model import CaseModel


class ApiImplementation(Api):

    def __init__(self,
                 case_model: CaseModel,
                 text_analyzer: TextAnalyzer,
                 case_handling_decision_engine: CaseHandlingDecisionEngine,
                 case_handling_distribution_engine: CaseHandlingDistributionEngine):

        self.case_model: CaseModel = case_model
        self.text_analyzer: TextAnalyzer = text_analyzer
        self.case_handling_decision_engine: CaseHandlingDecisionEngine = case_handling_decision_engine
        self.case_handling_distribution_engine: CaseHandlingDistributionEngine = case_handling_distribution_engine

    def get_case_model(self) -> CaseModel:
        return self.case_model

    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        return self.text_analyzer.analyze(field_values, text)

    def analyze_and_render(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        return self.text_analyzer.analyze_and_render(field_values, text)

    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingResponse:
        case_handling_decision: CaseHandlingDecision = self.case_handling_decision_engine.decide(request)
        case_handling_response: CaseHandlingResponse = self.case_handling_distribution_engine.distribute(self.case_model, request, case_handling_decision)
        return case_handling_response
