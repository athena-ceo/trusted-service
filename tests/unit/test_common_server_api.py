"""Tests unitaires pour ServerApi (interface abstraite)
Objectif : 90%+ de couverture.
"""

from abc import ABC

import pytest

from src.common.server_api import (
    CaseHandlingDecisionInput,
    CaseHandlingDecisionOutput,
    CaseHandlingDetailedResponse,
    CaseHandlingRequest,
    CaseHandlingResponse,
    ServerApi,
)


class TestServerApiInterface:
    """Tests pour l'interface ServerApi."""

    def test_server_api_is_abstract(self) -> None:
        """Test que ServerApi est une classe abstraite."""
        assert issubclass(ServerApi, ABC)

        # Tentative d'instanciation directe doit échouer
        with pytest.raises(TypeError):
            ServerApi()

    def test_server_api_has_all_abstract_methods(self) -> None:
        """Test que toutes les méthodes abstraites sont définies."""
        abstract_methods = {
            "reload_apps",
            "get_app_ids",
            "get_locales",
            "get_llm_config_ids",
            "get_decision_engine_config_ids",
            "get_app_name",
            "get_app_description",
            "get_sample_message",
            "get_case_model",
            "analyze",
            "save_text_analysis_cache",
            "handle_case",
        }

        # Vérifier que toutes les méthodes sont dans __abstractmethods__
        assert abstract_methods.issubset(ServerApi.__abstractmethods__)


class TestCaseHandlingModels:
    """Tests pour les modèles Pydantic."""

    def test_case_handling_request_creation(self) -> None:
        """Test création d'un CaseHandlingRequest."""
        request = CaseHandlingRequest(
            intention_id="intention1",
            field_values={"nom": "Dupont"},
            highlighted_text_and_features="<html>...</html>",
            decision_engine_config_id="engine1",
        )

        assert request.intention_id == "intention1"
        assert request.field_values == {"nom": "Dupont"}
        assert request.highlighted_text_and_features == "<html>...</html>"
        assert request.decision_engine_config_id == "engine1"

    def test_case_handling_request_empty_field_values(self) -> None:
        """Test CaseHandlingRequest avec field_values vide."""
        request = CaseHandlingRequest(
            intention_id="intention1",
            field_values={},
            highlighted_text_and_features="",
            decision_engine_config_id="engine1",
        )

        assert request.field_values == {}

    def test_case_handling_decision_input(self) -> None:
        """Test création d'un CaseHandlingDecisionInput."""
        decision_input = CaseHandlingDecisionInput(
            intention_id="intention1",
            field_values={"nom": "Dupont"},
        )

        assert decision_input.intention_id == "intention1"
        assert decision_input.field_values == {"nom": "Dupont"}

    def test_case_handling_decision_output(self) -> None:
        """Test création d'un CaseHandlingDecisionOutput."""
        decision_output = CaseHandlingDecisionOutput(
            handling="AUTOMATED",
            acknowledgement_to_requester="Merci",
            response_template_id="template1",
            work_basket="basket1",
            priority="MEDIUM",
            notes=["Note 1"],
            details={"decision_id": "123"},
        )

        assert decision_output.handling == "AUTOMATED"
        assert decision_output.priority == "MEDIUM"
        assert decision_output.acknowledgement_to_requester == "Merci"
        assert decision_output.response_template_id == "template1"
        assert decision_output.work_basket == "basket1"
        assert len(decision_output.notes) == 1
        assert decision_output.details == {"decision_id": "123"}

    def test_case_handling_decision_output_all_priorities(self) -> None:
        """Test toutes les valeurs de priority."""
        priorities = ["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]

        for priority in priorities:
            decision_output = CaseHandlingDecisionOutput(
                handling="AUTOMATED",
                acknowledgement_to_requester="Merci",
                response_template_id="template1",
                work_basket="basket1",
                priority=priority,
                notes=[],
            )
            assert decision_output.priority == priority

    def test_case_handling_decision_output_all_handling_types(self) -> None:
        """Test toutes les valeurs de handling."""
        handling_types = ["AUTOMATED", "AGENT", "DEFLECTION"]

        for handling in handling_types:
            decision_output = CaseHandlingDecisionOutput(
                handling=handling,
                acknowledgement_to_requester="Merci",
                response_template_id="template1",
                work_basket="basket1",
                priority="MEDIUM",
                notes=[],
            )
            assert decision_output.handling == handling

    def test_case_handling_decision_output_empty_notes(self) -> None:
        """Test CaseHandlingDecisionOutput avec notes vide."""
        decision_output = CaseHandlingDecisionOutput(
            handling="AUTOMATED",
            acknowledgement_to_requester="Merci",
            response_template_id="template1",
            work_basket="basket1",
            priority="MEDIUM",
            notes=[],
        )

        assert decision_output.notes == []

    def test_case_handling_decision_output_multiple_notes(self) -> None:
        """Test CaseHandlingDecisionOutput avec plusieurs notes."""
        decision_output = CaseHandlingDecisionOutput(
            handling="AUTOMATED",
            acknowledgement_to_requester="Merci",
            response_template_id="template1",
            work_basket="basket1",
            priority="MEDIUM",
            notes=["Note 1", "Note 2", "Note 3"],
        )

        assert len(decision_output.notes) == 3

    def test_case_handling_response(self) -> None:
        """Test création d'un CaseHandlingResponse."""
        response = CaseHandlingResponse(
            acknowledgement_to_requester="Merci",
            case_handling_report=("Agent mail", "Requester mail"),
        )

        assert response.acknowledgement_to_requester == "Merci"
        assert len(response.case_handling_report) == 2
        assert response.case_handling_report[0] == "Agent mail"
        assert response.case_handling_report[1] == "Requester mail"

    def test_case_handling_response_none_requester(self) -> None:
        """Test CaseHandlingResponse avec requester mail à None."""
        response = CaseHandlingResponse(
            acknowledgement_to_requester="Merci",
            case_handling_report=("Agent mail", None),
        )

        assert response.case_handling_report[0] == "Agent mail"
        assert response.case_handling_report[1] is None

    def test_case_handling_detailed_response(self) -> None:
        """Test création d'un CaseHandlingDetailedResponse."""
        decision_input = CaseHandlingDecisionInput(
            intention_id="intention1",
            field_values={},
        )
        decision_output = CaseHandlingDecisionOutput(
            handling="AUTOMATED",
            acknowledgement_to_requester="Merci",
            response_template_id="template1",
            work_basket="basket1",
            priority="MEDIUM",
            notes=[],
        )
        case_response = CaseHandlingResponse(
            acknowledgement_to_requester="Merci",
            case_handling_report=("Agent", "Requester"),
        )

        detailed = CaseHandlingDetailedResponse(
            case_handling_decision_input=decision_input,
            case_handling_decision_output=decision_output,
            case_handling_response=case_response,
        )

        assert detailed.case_handling_decision_input == decision_input
        assert detailed.case_handling_decision_output == decision_output
        assert detailed.case_handling_response == case_response

    def test_case_handling_models_validation_errors(self) -> None:
        """Test que les modèles rejettent les valeurs invalides."""
        # Priority invalide
        with pytest.raises(Exception):  # ValidationError ou ValueError selon Pydantic
            CaseHandlingDecisionOutput(
                handling="AUTOMATED",
                acknowledgement_to_requester="Merci",
                response_template_id="template1",
                work_basket="basket1",
                priority="INVALID",  # Valeur invalide
                notes=[],
            )

        # Handling invalide
        with pytest.raises(Exception):
            CaseHandlingDecisionOutput(
                handling="INVALID",  # Valeur invalide
                acknowledgement_to_requester="Merci",
                response_template_id="template1",
                work_basket="basket1",
                priority="MEDIUM",
                notes=[],
            )
