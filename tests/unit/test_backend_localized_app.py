"""Tests unitaires pour LocalizedApp
Objectif : 90%+ de couverture
Focus : Mécanisme de retry et fallback.
"""

from unittest.mock import Mock, patch

import pytest

from src.backend.backend.localized_app import LocalizedApp
from src.backend.text_analysis.base_models import FIELD_NAME_SCORINGS
from src.backend.text_analysis.llm import LlmConfig
from src.common.constants import (
    KEY_ANALYSIS_RESULT,
    KEY_HIGHLIGHTED_TEXT_AND_FEATURES,
    KEY_MARKDOWN_TABLE,
    KEY_PROMPT,
    KEY_STATISTICS,
)


class TestLocalizedAppFallback:
    """Tests pour _create_fallback_response()."""

    def test_create_fallback_response_fr(self) -> None:
        """Test création réponse fallback en français."""
        from src.backend.backend.localized_app import LocalizedApp

        # Créer un mock LlmConfig
        llm_config = Mock(spec=LlmConfig)
        llm_config.id = "test_config"
        llm_config.llm = "openai"
        llm_config.model = "gpt-4"
        llm_config.prompt_format = "markdown"

        exception = ValueError("Test error message")

        # Créer une instance minimale de LocalizedApp pour tester la méthode
        # On va créer un mock de LocalizedApp avec juste la méthode qu'on veut tester
        with patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None):
            app = LocalizedApp(None, None, None, None)
            response = app._create_fallback_response("fr", llm_config, exception)

            # Vérifications
            assert KEY_ANALYSIS_RESULT in response
            assert KEY_PROMPT in response
            assert KEY_MARKDOWN_TABLE in response
            assert KEY_HIGHLIGHTED_TEXT_AND_FEATURES in response

            analysis_result = response[KEY_ANALYSIS_RESULT]
            assert FIELD_NAME_SCORINGS in analysis_result
            assert len(analysis_result[FIELD_NAME_SCORINGS]) == 1

            scoring = analysis_result[FIELD_NAME_SCORINGS][0]
            assert scoring["intention_id"] == "other"
            assert scoring["score"] == 1
            assert scoring["intention_label"] == "AUTRE"  # En français
            assert "Erreur lors de l'analyse" in scoring["justification"]

            # Vérifier les statistiques
            assert KEY_STATISTICS in analysis_result
            stats = analysis_result[KEY_STATISTICS]
            assert "Error code" in stats
            assert "Error Message" in stats
            assert "ValueError" in stats["Error code"]
            assert "Test error message" in stats["Error Message"]

    def test_create_fallback_response_en(self) -> None:
        """Test création réponse fallback en anglais."""
        from src.backend.backend.localized_app import LocalizedApp

        llm_config = Mock(spec=LlmConfig)
        llm_config.id = "test_config"
        llm_config.llm = "openai"
        llm_config.model = "gpt-4"
        llm_config.prompt_format = "markdown"

        exception = ValueError("Test error")

        with patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None):
            app = LocalizedApp(None, None, None, None)
            response = app._create_fallback_response("en", llm_config, exception)

            analysis_result = response[KEY_ANALYSIS_RESULT]
            scoring = analysis_result[FIELD_NAME_SCORINGS][0]
            assert scoring["intention_label"] == "OTHER"  # En anglais
            assert "Analysis error" in scoring["justification"]

    def test_create_fallback_response_error_message_contains_traceback(self) -> None:
        """Test que Error Message contient le traceback complet."""
        from src.backend.backend.localized_app import LocalizedApp

        llm_config = Mock(spec=LlmConfig)
        llm_config.id = "test_config"
        llm_config.llm = "openai"
        llm_config.model = "gpt-4"
        llm_config.prompt_format = "markdown"

        exception = ValueError("Test error with details")

        with patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None):
            app = LocalizedApp(None, None, None, None)
            response = app._create_fallback_response("fr", llm_config, exception)

            analysis_result = response[KEY_ANALYSIS_RESULT]
            stats = analysis_result[KEY_STATISTICS]

            assert "Error Message" in stats
            error_message = stats["Error Message"]
            assert "ValueError" in error_message
            assert "Test error with details" in error_message
            assert "Traceback" in error_message


class TestLocalizedAppAnalyzeRetry:
    """Tests pour le mécanisme de retry dans analyze()."""

    @pytest.fixture()
    def mock_llm_config(self):
        """Fixture pour LlmConfig."""
        config = Mock(spec=LlmConfig)
        config.id = "test_config"
        config.llm = "openai"
        config.model = "gpt-4"
        config.prompt_format = "markdown"
        return config

    @patch("time.sleep")  # Mock sleep pour accélérer les tests
    def test_analyze_success_first_try(self, mock_sleep, mock_llm_config) -> None:
        """Test que analyze() réussit au premier essai."""
        # Mock TextAnalyzer
        mock_result = {
            KEY_ANALYSIS_RESULT: {FIELD_NAME_SCORINGS: [], KEY_STATISTICS: {}},
        }
        mock_text_analyzer = Mock()
        mock_text_analyzer.analyze.return_value = mock_result

        # Créer une vraie instance pour tester
        with patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None):
            app = LocalizedApp(None, None, None, None)
            app.text_analyzer = mock_text_analyzer
            app.parent_app = Mock()
            app.parent_app.llm_configs = {"test_config": mock_llm_config}

            result = app.analyze(
                app_id="test_app",
                locale="fr",
                field_values={},
                text="Test text",
                read_from_cache=False,
                llm_config_id="test_config",
            )

            assert result == mock_result
            assert mock_sleep.call_count == 0  # Pas de retry

    @patch("time.sleep")
    def test_analyze_retry_on_error(self, mock_sleep, mock_llm_config) -> None:
        """Test que analyze() réessaie après une erreur."""
        # Premier appel échoue, deuxième réussit
        mock_result = {
            KEY_ANALYSIS_RESULT: {FIELD_NAME_SCORINGS: [], KEY_STATISTICS: {}},
        }
        mock_text_analyzer = Mock()
        mock_text_analyzer.analyze.side_effect = [
            ValueError("First error"),
            mock_result,
        ]

        with patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None):
            app = LocalizedApp(None, None, None, None)
            app.text_analyzer = mock_text_analyzer
            app.parent_app = Mock()
            app.parent_app.llm_configs = {"test_config": mock_llm_config}

            result = app.analyze(
                app_id="test_app",
                locale="fr",
                field_values={},
                text="Test text",
                read_from_cache=False,
                llm_config_id="test_config",
            )

            assert result == mock_result
            assert mock_text_analyzer.analyze.call_count == 2
            assert mock_sleep.call_count == 1  # Un retry

    @patch("time.sleep")
    def test_analyze_returns_fallback_after_3_failures(
        self,
        mock_sleep,
        mock_llm_config,
    ) -> None:
        """Test que analyze() retourne fallback après 3 échecs."""
        mock_text_analyzer = Mock()
        mock_text_analyzer.analyze.side_effect = ValueError("Persistent error")

        with patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None):
            app = LocalizedApp(None, None, None, None)
            app.text_analyzer = mock_text_analyzer
            app.parent_app = Mock()
            app.parent_app.llm_configs = {"test_config": mock_llm_config}

            result = app.analyze(
                app_id="test_app",
                locale="fr",
                field_values={},
                text="Test text",
                read_from_cache=False,
                llm_config_id="test_config",
            )

            assert mock_text_analyzer.analyze.call_count == 3
            assert mock_sleep.call_count == 2  # 2 retries

            # Vérifier que c'est une réponse de fallback
            assert KEY_ANALYSIS_RESULT in result
            analysis_result = result[KEY_ANALYSIS_RESULT]
            assert FIELD_NAME_SCORINGS in analysis_result
            assert len(analysis_result[FIELD_NAME_SCORINGS]) == 1
            assert analysis_result[FIELD_NAME_SCORINGS][0]["intention_id"] == "other"
            assert analysis_result[FIELD_NAME_SCORINGS][0]["score"] == 1
            assert "Error code" in analysis_result[KEY_STATISTICS]
            assert "Error Message" in analysis_result[KEY_STATISTICS]

    @patch("time.sleep")
    def test_analyze_retry_delay_2_seconds(self, mock_sleep, mock_llm_config) -> None:
        """Test que le délai entre retries est de 2 secondes."""
        mock_result = {
            KEY_ANALYSIS_RESULT: {FIELD_NAME_SCORINGS: [], KEY_STATISTICS: {}},
        }
        mock_text_analyzer = Mock()
        mock_text_analyzer.analyze.side_effect = [
            ValueError("Error 1"),
            ValueError("Error 2"),
            mock_result,
        ]

        with patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None):
            app = LocalizedApp(None, None, None, None)
            app.text_analyzer = mock_text_analyzer
            app.parent_app = Mock()
            app.parent_app.llm_configs = {"test_config": mock_llm_config}

            app.analyze(
                app_id="test_app",
                locale="fr",
                field_values={},
                text="Test text",
                read_from_cache=False,
                llm_config_id="test_config",
            )

            # Vérifier que sleep a été appelé avec 2.0
            assert mock_sleep.call_count == 2
            for call in mock_sleep.call_args_list:
                assert call[0][0] == 2.0

    @patch("time.sleep")
    def test_analyze_different_exception_types(
        self, mock_sleep, mock_llm_config
    ) -> None:
        """Test que différents types d'exceptions sont gérés et retournent fallback après 3 échecs."""
        exceptions = [
            ValueError("Value error"),
            KeyError("Key error"),
            RuntimeError("Runtime error"),
        ]

        mock_text_analyzer = Mock()
        mock_text_analyzer.analyze.side_effect = exceptions  # 3 erreurs, pas de succès

        with patch.object(LocalizedApp, "__init__", lambda self, *args, **kwargs: None):
            app = LocalizedApp(None, None, None, None)
            app.text_analyzer = mock_text_analyzer
            app.parent_app = Mock()
            app.parent_app.llm_configs = {"test_config": mock_llm_config}

            result = app.analyze(
                app_id="test_app",
                locale="fr",
                field_values={},
                text="Test text",
                read_from_cache=False,
                llm_config_id="test_config",
            )

            # Après 3 échecs, doit retourner une réponse de fallback
            assert mock_text_analyzer.analyze.call_count == 3
            assert mock_sleep.call_count == 2  # 2 retries

            # Vérifier que c'est une réponse de fallback
            assert KEY_ANALYSIS_RESULT in result
            analysis_result = result[KEY_ANALYSIS_RESULT]
            assert FIELD_NAME_SCORINGS in analysis_result
            assert len(analysis_result[FIELD_NAME_SCORINGS]) == 1
            assert analysis_result[FIELD_NAME_SCORINGS][0]["intention_id"] == "other"
            assert "Error code" in analysis_result[KEY_STATISTICS]
            # Vérifier que le dernier type d'erreur est dans le code d'erreur
            assert "RuntimeError" in analysis_result[KEY_STATISTICS]["Error code"]
