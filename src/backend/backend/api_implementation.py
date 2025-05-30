from typing import Any

from src.backend.decision.decision import CaseHandlingDecisionEngine
from src.backend.distribution.distribution import CaseHandlingDistributionEngine
from src.backend.text_analysis.text_analyzer import TextAnalyzer
from src.common.api import Api, CaseHandlingRequest, CaseHandlingResponse, CaseHandlingDetailedResponse, CaseHandlingDecisionInput, CaseHandlingDecisionOutput
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

    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:

        # Filter-out the field values that are not to be sent to the decision engine
        field_values: dict[str, Any] = {}
        for case_field in self.case_model.case_fields:
            if case_field.send_to_decision_engine:
                field_values[case_field.id] = request.field_values[case_field.id]

        case_handling_decision_input = CaseHandlingDecisionInput(intention_id=request.intention_id, field_values=field_values)
        case_handling_decision_output: CaseHandlingDecisionOutput = self.case_handling_decision_engine.decide(case_handling_decision_input)
        case_handling_response: CaseHandlingResponse = self.case_handling_distribution_engine.distribute(self.case_model, request, case_handling_decision_output)

        return CaseHandlingDetailedResponse(case_handling_decision_input=case_handling_decision_input,
                                            case_handling_decision_output=case_handling_decision_output,
                                            case_handling_response=case_handling_response)
