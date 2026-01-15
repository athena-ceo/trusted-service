"""Tests unitaires pour ApiClientRest
Objectif : 90%+ de couverture.
"""

from unittest.mock import Mock, patch

import pytest

from src.client.api_client_rest import ApiClientRest
from src.common.case_model import CaseModel
from src.common.constants import API_ROUTE_V2


class TestApiClientRestInit:
    """Tests pour __init__()."""

    def test_init_sets_base_url(self) -> None:
        """Test que __init__ définit base_url."""
        client = ApiClientRest("http://localhost:8002")
        assert client.base_url == "http://localhost:8002"

    def test_init_with_different_urls(self) -> None:
        """Test __init__ avec différentes URLs."""
        urls = [
            "http://localhost:8002",
            "https://api.example.com",
            "http://127.0.0.1:8080",
        ]

        for url in urls:
            client = ApiClientRest(url)
            assert client.base_url == url


class TestApiClientRestGet:
    """Tests pour get()."""

    @pytest.fixture()
    def client(self):
        return ApiClientRest("http://localhost:8002")

    @patch("src.client.api_client_rest.requests.get")
    def test_get_simple(self, mock_get, client) -> None:
        """Test get() simple."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "test"}
        mock_get.return_value = mock_response

        result = client.get("app_ids")

        assert result == {"result": "test"}
        mock_get.assert_called_once()
        url = mock_get.call_args[0][0]
        assert API_ROUTE_V2 in url
        assert "app_ids" in url

    @patch("src.client.api_client_rest.requests.get")
    def test_get_with_app_id(self, mock_get, client) -> None:
        """Test get() avec app_id."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["fr", "en"]
        mock_get.return_value = mock_response

        result = client.get("locales", app_id="delphes78")

        assert result == ["fr", "en"]
        url = mock_get.call_args[0][0]
        assert "/apps/delphes78" in url
        assert "locales" in url

    @patch("src.client.api_client_rest.requests.get")
    def test_get_with_app_id_and_locale(self, mock_get, client) -> None:
        """Test get() avec app_id et locale."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Delphes"}
        mock_get.return_value = mock_response

        result = client.get("app_name", app_id="delphes78", locale="fr")

        assert result == {"name": "Delphes"}
        url = mock_get.call_args[0][0]
        assert "/apps/delphes78/fr" in url
        assert "app_name" in url

    @patch("src.client.api_client_rest.requests.get")
    def test_get_error_status(self, mock_get, client) -> None:
        """Test get() avec status code d'erreur."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = client.get("app_ids")

        # Selon l'implémentation actuelle, get() retourne None en cas d'erreur
        assert result is None

    @patch("src.client.api_client_rest.requests.get")
    def test_get_500_error(self, mock_get, client) -> None:
        """Test get() avec erreur 500."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = client.get("app_ids")

        assert result is None


class TestApiClientRestAnalyze:
    """Tests pour analyze()."""

    @pytest.fixture()
    def client(self):
        return ApiClientRest("http://localhost:8002")

    @patch("src.client.api_client_rest.requests.post")
    def test_analyze_success(self, mock_post, client) -> None:
        """Test analyze() avec succès."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"analysis_result": {"scorings": []}}
        mock_post.return_value = mock_response

        result = client.analyze(
            app_id="delphes78",
            locale="fr",
            field_values={},
            text="Test text",
            read_from_cache=False,
            llm_config_id="scaleway1",
        )

        assert "analysis_result" in result
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/apps/delphes78/fr/analyze" in call_args[0][0]
        assert call_args[1]["json"]["text"] == "Test text"
        assert call_args[1]["json"]["field_values"] == {}
        assert call_args[1]["json"]["read_from_cache"] is False
        assert call_args[1]["json"]["llm_config_id"] == "scaleway1"

    @patch("src.client.api_client_rest.requests.post")
    def test_analyze_with_field_values(self, mock_post, client) -> None:
        """Test analyze() avec field_values."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"analysis_result": {}}
        mock_post.return_value = mock_response

        field_values = {"nom": "Dupont", "prenom": "Jean"}

        client.analyze(
            app_id="delphes78",
            locale="fr",
            field_values=field_values,
            text="Test",
            read_from_cache=True,
            llm_config_id="scaleway1",
        )

        call_args = mock_post.call_args
        assert call_args[1]["json"]["field_values"] == field_values
        assert call_args[1]["json"]["read_from_cache"] is True

    @patch("src.client.api_client_rest.requests.post")
    def test_analyze_error(self, mock_post, client) -> None:
        """Test analyze() avec erreur."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = client.analyze(
            app_id="delphes78",
            locale="fr",
            field_values={},
            text="Test",
            read_from_cache=False,
            llm_config_id="scaleway1",
        )

        assert result is None


class TestApiClientRestOtherMethods:
    """Tests pour les autres méthodes."""

    @pytest.fixture()
    def client(self):
        return ApiClientRest("http://localhost:8002")

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_app_ids(self, mock_get, client) -> None:
        """Test get_app_ids()."""
        mock_get.return_value = ["delphes78", "delphes91"]
        result = client.get_app_ids()
        assert result == ["delphes78", "delphes91"]
        mock_get.assert_called_once_with("app_ids")

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_locales(self, mock_get, client) -> None:
        """Test get_locales()."""
        mock_get.return_value = ["fr", "en"]
        result = client.get_locales("delphes78")
        assert result == ["fr", "en"]
        mock_get.assert_called_once_with("locales", "delphes78")

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_llm_config_ids(self, mock_get, client) -> None:
        """Test get_llm_config_ids()."""
        mock_get.return_value = ["scaleway1", "openai1"]
        result = client.get_llm_config_ids("delphes78")
        assert result == ["scaleway1", "openai1"]
        mock_get.assert_called_once_with("llm_config_ids", "delphes78")

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_decision_engine_config_ids(self, mock_get, client) -> None:
        """Test get_decision_engine_config_ids()."""
        mock_get.return_value = ["engine1"]
        result = client.get_decision_engine_config_ids("delphes78")
        assert result == ["engine1"]
        mock_get.assert_called_once_with("decision_engine_config_ids", "delphes78")

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_app_name(self, mock_get, client) -> None:
        """Test get_app_name()."""
        mock_get.return_value = "Delphes"
        result = client.get_app_name("delphes78", "fr")
        assert result == "Delphes"
        mock_get.assert_called_once_with("app_name", "delphes78", "fr")

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_app_description(self, mock_get, client) -> None:
        """Test get_app_description()."""
        mock_get.return_value = "Description"
        result = client.get_app_description("delphes78", "fr")
        assert result == "Description"
        mock_get.assert_called_once_with("app_description", "delphes78", "fr")

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_sample_message(self, mock_get, client) -> None:
        """Test get_sample_message()."""
        mock_get.return_value = "Sample message"
        result = client.get_sample_message("delphes78", "fr")
        assert result == "Sample message"
        mock_get.assert_called_once_with("sample_message", "delphes78", "fr")

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_case_model(self, mock_get, client) -> None:
        """Test get_case_model()."""
        mock_get.return_value = {
            "case_fields": [
                {
                    "id": "nom",
                    "type": "str",
                    "label": "Nom",
                    "mandatory": True,
                    "help": "",
                    "format": "",
                    "allowed_values_list_name": "",
                    "allowed_values": [],
                    "default_value": None,
                    "scope": "REQUESTER",
                    "show_in_ui": True,
                    "intention_ids": [],
                    "description": "Nom",
                    "extraction": "EXTRACT",
                    "send_to_decision_engine": True,
                },
            ],
        }

        result = client.get_case_model("delphes78", "fr")

        assert result is not None
        assert isinstance(result, CaseModel)
        assert len(result.case_fields) == 1
        assert result.case_fields[0].id == "nom"

    @patch("src.client.api_client_rest.ApiClientRest.get")
    def test_get_case_model_none(self, mock_get, client) -> None:
        """Test get_case_model() avec None."""
        mock_get.return_value = None

        result = client.get_case_model("delphes78", "fr")

        assert result is None


class TestApiClientRestReloadAndSave:
    """Tests pour reload_apps() et save_text_analysis_cache()."""

    @pytest.fixture()
    def client(self):
        return ApiClientRest("http://localhost:8002")

    @patch("src.client.api_client_rest.requests.post")
    def test_reload_apps_success(self, mock_post, client) -> None:
        """Test reload_apps() avec succès."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        result = client.reload_apps()

        assert result == {"status": "ok"}
        mock_post.assert_called_once()
        assert "/reload_apps" in mock_post.call_args[0][0]

    @patch("src.client.api_client_rest.requests.post")
    def test_reload_apps_error(self, mock_post, client) -> None:
        """Test reload_apps() avec erreur."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = client.reload_apps()

        assert result is None

    @patch("src.client.api_client_rest.requests.post")
    def test_save_text_analysis_cache_success(self, mock_post, client) -> None:
        """Test save_text_analysis_cache() avec succès."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "saved"}
        mock_post.return_value = mock_response

        cache_data = '{"hash_code": "abc123", "result": {}}'
        result = client.save_text_analysis_cache("delphes78", "fr", cache_data)

        assert result == {"status": "saved"}
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/apps/delphes78/fr/save_text_analysis_cache" in call_args[0][0]
        assert call_args[1]["params"]["text_analysis_cache"] == cache_data

    @patch("src.client.api_client_rest.requests.post")
    def test_save_text_analysis_cache_error(self, mock_post, client) -> None:
        """Test save_text_analysis_cache() avec erreur."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        result = client.save_text_analysis_cache("delphes78", "fr", "{}")

        assert result is None


class TestApiClientRestHandleCase:
    """Tests pour handle_case()."""

    @pytest.fixture()
    def client(self):
        return ApiClientRest("http://localhost:8002")

    @patch("src.client.api_client_rest.requests.post")
    def test_handle_case_success(self, mock_post, client) -> None:
        """Test handle_case() avec succès."""
        from src.common.server_api import CaseHandlingRequest

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "case_handling_decision_input": {
                "intention_id": "intention1",
                "field_values": {},
            },
            "case_handling_decision_output": {
                "handling": "AUTOMATED",
                "acknowledgement_to_requester": "Merci",
                "response_template_id": "template1",
                "work_basket": "basket1",
                "priority": "MEDIUM",
                "notes": [],
            },
            "case_handling_response": {
                "acknowledgement_to_requester": "Merci",
                "case_handling_report": ["Agent mail", "Requester mail"],
            },
        }
        mock_post.return_value = mock_response

        request = CaseHandlingRequest(
            intention_id="intention1",
            field_values={},
            highlighted_text_and_features="<html></html>",
            decision_engine_config_id="engine1",
        )

        result = client.handle_case("delphes78", "fr", request)

        assert result is not None
        assert result.case_handling_decision_output.handling == "AUTOMATED"
        mock_post.assert_called_once()
        assert "/apps/delphes78/fr/handle_case" in mock_post.call_args[0][0]

    @patch("src.client.api_client_rest.requests.post")
    def test_handle_case_error(self, mock_post, client) -> None:
        """Test handle_case() avec erreur."""
        from src.common.server_api import CaseHandlingRequest

        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        request = CaseHandlingRequest(
            intention_id="intention1",
            field_values={},
            highlighted_text_and_features="",
            decision_engine_config_id="engine1",
        )

        result = client.handle_case("delphes78", "fr", request)

        assert result is None
