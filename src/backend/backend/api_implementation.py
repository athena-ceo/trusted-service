import json
from typing import Any

from src.backend.backend.backend_configuration import Message
from src.backend.decision.decision import CaseHandlingDecisionEngine
from src.backend.distribution.distribution import CaseHandlingDistributionEngine
from src.backend.text_analysis.text_analyzer import TextAnalyzer
from src.common.api import Api, CaseHandlingRequest, CaseHandlingResponse, CaseHandlingDetailedResponse, CaseHandlingDecisionInput, CaseHandlingDecisionOutput
from src.common.case_model import CaseModel


class ApiImplementation(Api):

    def __init__(self,
                 app_name: str,
                 app_description: str,
                 messages_to_agent: list[Message],
                 messages_to_requester: list[Message],
                 case_model: CaseModel,
                 text_analyzer: TextAnalyzer,
                 case_handling_decision_engine: CaseHandlingDecisionEngine,
                 case_handling_distribution_engine: CaseHandlingDistributionEngine):
        self.app_name = app_name
        self.app_description = app_description
        self.messages_to_agent = messages_to_agent
        self.messages_to_requester = messages_to_requester
        self.case_model: CaseModel = case_model
        self.text_analyzer: TextAnalyzer = text_analyzer
        self.case_handling_decision_engine: CaseHandlingDecisionEngine = case_handling_decision_engine
        self.case_handling_distribution_engine: CaseHandlingDistributionEngine = case_handling_distribution_engine

    def get_app_name(self) -> str:
        return self.app_name

    def get_app_description(self) -> str:
        return self.app_description

    def get_case_model(self) -> CaseModel:
        return self.case_model

    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, Any]:
        result = self.text_analyzer.analyze(field_values, text)
        return result

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

    def handle_case(self, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:

        # Filter-out the field values that are not to be sent to the decision engine
        field_values: dict[str, Any] = {}
        for case_field in self.case_model.case_fields:
            if case_field.send_to_decision_engine:
                field_values[case_field.id] = request.field_values[case_field.id]

        case_handling_decision_input = CaseHandlingDecisionInput(intention_id=request.intention_id, field_values=field_values)

        case_handling_decision_output: CaseHandlingDecisionOutput = self.case_handling_decision_engine.decide(case_handling_decision_input)

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
