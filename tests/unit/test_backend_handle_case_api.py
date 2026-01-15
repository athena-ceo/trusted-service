"""Tests supplémentaires sur LocalizedApp.handle_case pour valider:
- la validation des champs requis envoyés au moteur de décision
- la gestion d'un moteur de distribution non configuré.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.backend.backend.localized_app import LocalizedApp, Message
from src.backend.text_analysis.base_models import Definition, Intention
from src.backend.text_analysis.text_analyzer import TextAnalysisConfig
from src.common.case_model import CaseField, CaseModel
from src.common.server_api import CaseHandlingDecisionOutput, CaseHandlingRequest


class DummyDistributionEngine:
    def __init__(self, response=("to_agent", "to_requester")) -> None:
        self.response = response

    def distribute(self, *args, **kwargs):
        return self.response


def _build_case_model(field_id: str) -> CaseModel:
    return CaseModel(
        case_fields=[
            CaseField(
                id=field_id,
                type="str",
                label="Field",
                mandatory=True,
                help="",
                format="",
                allowed_values_list_name="",
                allowed_values=[],
                default_value=None,
                scope="REQUESTER",
                show_in_ui=True,
                intention_ids=["intent1"],
                description="",
                extraction="EXTRACT",
                send_to_decision_engine=True,
            ),
        ],
    )


def _build_text_analysis_config() -> TextAnalysisConfig:
    return TextAnalysisConfig(
        system_prompt_prefix="",
        definitions=[Definition(term="t", definition="d")],
        intentions=[Intention(id="intent1", label="Intent 1", description="Desc")],
    )


def _build_request(field_id: str, include_field: bool) -> CaseHandlingRequest:
    field_values = {field_id: "value"} if include_field else {}
    return CaseHandlingRequest(
        intention_id="intent1",
        field_values=field_values,
        highlighted_text_and_features="",
        decision_engine_config_id="dec1",
    )


def _build_decision_output() -> CaseHandlingDecisionOutput:
    return CaseHandlingDecisionOutput(
        handling="AGENT",
        acknowledgement_to_requester="#ack",
        response_template_id="tpl",
        work_basket="default",
        priority="MEDIUM",
        notes=["#note,foo"],
        details=None,
    )


@patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None)
def test_handle_case_missing_required_fields_raises_value_error() -> None:
    app = LocalizedApp(None, None, None, None)
    field_id = "required_field"
    app.case_model = _build_case_model(field_id)
    app.text_analysis_config = _build_text_analysis_config()
    app.parent_app = MagicMock()
    app.parent_app.data_enrichment = None
    app.parent_app.decide = MagicMock(return_value=_build_decision_output())
    app.case_handling_distribution_engine = DummyDistributionEngine()
    app.messages_to_agent = [Message(key="note", text="Note")]
    app.messages_to_requester = [Message(key="ack", text="Ack")]

    request = _build_request(field_id, include_field=False)

    with pytest.raises(ValueError) as exc:
        app.handle_case(app_id="app", locale="fr", request=request)

    assert field_id in str(exc.value)
    app.parent_app.decide.assert_not_called()


@patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None)
def test_handle_case_without_distribution_engine_returns_error_before_distribute() -> (
    None
):
    app = LocalizedApp(None, None, None, None)
    field_id = "required_field"
    app.case_model = _build_case_model(field_id)
    app.text_analysis_config = _build_text_analysis_config()
    app.parent_app = MagicMock()
    app.parent_app.data_enrichment = None
    app.parent_app.decide = MagicMock(return_value=_build_decision_output())
    app.case_handling_distribution_engine = None
    app.messages_to_agent = [Message(key="note", text="Note")]
    app.messages_to_requester = [Message(key="ack", text="Ack")]

    request = _build_request(field_id, include_field=True)

    with pytest.raises(ValueError) as exc:
        app.handle_case(app_id="app", locale="fr", request=request)

    assert "distribution engine" in str(exc.value)
    app.parent_app.decide.assert_called_once()
