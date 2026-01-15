"""Tests unitaires pour TextAnalyzer
Objectif : 90%+ de couverture.
"""

import json
import os
from unittest.mock import Mock, patch

import pytest

from src.backend.text_analysis.base_models import FIELD_NAME_SCORINGS, Feature
from src.backend.text_analysis.llm import LlmConfig
from src.backend.text_analysis.text_analyzer import TextAnalyzer, create_analysis_models
from src.common.case_model import CaseField, CaseModel
from src.common.constants import (
    KEY_ANALYSIS_RESULT,
    KEY_HASH_CODE,
    KEY_HIGHLIGHTED_TEXT_AND_FEATURES,
    KEY_MARKDOWN_TABLE,
    KEY_PROMPT,
    KEY_STATISTICS,
)


class TestCreateAnalysisModels:
    """Tests pour create_analysis_models()."""

    def test_create_analysis_models_fr(self) -> None:
        """Test création de modèles d'analyse en français."""
        locale = "fr"
        features = [
            Feature(
                id="nom",
                label="Nom",
                type=str,
                description="Nom de famille",
                highlight_fragments=False,
            ),
        ]

        model_class = create_analysis_models(locale, features)

        # Vérifier que le modèle peut être instancié
        instance = model_class(scorings=[])
        assert hasattr(instance, "scorings")
        assert hasattr(instance, "nom")

    def test_create_analysis_models_with_highlight(self) -> None:
        """Test création avec highlight_fragments=True."""
        locale = "en"
        features = [
            Feature(
                id="date",
                label="Date",
                type=str,
                description="Date of birth",
                highlight_fragments=True,
            ),
        ]

        model_class = create_analysis_models(locale, features)
        instance = model_class(scorings=[])

        # Vérifier que fragments_date existe
        assert hasattr(instance, "fragments_date")

    def test_create_analysis_models_multiple_features(self) -> None:
        """Test création avec plusieurs features."""
        locale = "fr"
        features = [
            Feature(
                id="nom",
                label="Nom",
                type=str,
                description="Nom",
                highlight_fragments=False,
            ),
            Feature(
                id="prenom",
                label="Prénom",
                type=str,
                description="Prénom",
                highlight_fragments=True,
            ),
        ]

        model_class = create_analysis_models(locale, features)
        instance = model_class(scorings=[])

        assert hasattr(instance, "nom")
        assert hasattr(instance, "prenom")
        assert hasattr(instance, "fragments_prenom")


class TestTextAnalyzerInit:
    """Tests pour __init__()."""

    def test_init_creates_features(
        self,
        sample_case_model,
        sample_text_analysis_config,
        temp_runtime_directory,
    ) -> None:
        """Test que __init__ crée les features correctement."""
        analyzer = TextAnalyzer(
            runtime_directory=temp_runtime_directory,
            app_id="test_app",
            locale="fr",
            case_model=sample_case_model,
            text_analysis_config=sample_text_analysis_config,
        )

        assert len(analyzer.features) == 1
        assert analyzer.features[0].id == "nom"
        assert analyzer.features[0].label == "Nom"

    def test_init_excludes_do_not_extract(
        self,
        sample_text_analysis_config,
        temp_runtime_directory,
    ) -> None:
        """Test que les champs avec extraction='DO NOT EXTRACT' sont exclus."""
        case_field = CaseField(
            id="internal_id",
            type="str",
            label="ID interne",
            mandatory=True,
            help="",
            format="",
            allowed_values_list_name="",
            allowed_values=[],
            default_value=None,
            scope="CONTEXT",
            show_in_ui=False,
            intention_ids=[],
            description="ID interne",
            extraction="DO NOT EXTRACT",
            send_to_decision_engine=False,
        )
        case_model = CaseModel(case_fields=[case_field])

        analyzer = TextAnalyzer(
            runtime_directory=temp_runtime_directory,
            app_id="test_app",
            locale="fr",
            case_model=case_model,
            text_analysis_config=sample_text_analysis_config,
        )

        assert len(analyzer.features) == 0

    def test_init_includes_extract_and_highlight(
        self,
        sample_text_analysis_config,
        temp_runtime_directory,
    ) -> None:
        """Test que les champs avec extraction='EXTRACT AND HIGHLIGHT' ont highlight_fragments=True."""
        case_field = CaseField(
            id="date",
            type="str",
            label="Date",
            mandatory=True,
            help="",
            format="",
            allowed_values_list_name="",
            allowed_values=[],
            default_value=None,
            scope="REQUESTER",
            show_in_ui=True,
            intention_ids=[],
            description="Date de naissance",
            extraction="EXTRACT AND HIGHLIGHT",
            send_to_decision_engine=True,
        )
        case_model = CaseModel(case_fields=[case_field])

        analyzer = TextAnalyzer(
            runtime_directory=temp_runtime_directory,
            app_id="test_app",
            locale="fr",
            case_model=case_model,
            text_analysis_config=sample_text_analysis_config,
        )

        assert len(analyzer.features) == 1
        assert analyzer.features[0].highlight_fragments is True


class TestTextAnalyzerAnalyze:
    """Tests pour analyze() et _analyze()."""

    @pytest.fixture()
    def analyzer(
        self,
        sample_case_model,
        sample_text_analysis_config,
        temp_runtime_directory,
    ):
        """Fixture pour TextAnalyzer."""
        return TextAnalyzer(
            runtime_directory=temp_runtime_directory,
            app_id="test_app",
            locale="fr",
            case_model=sample_case_model,
            text_analysis_config=sample_text_analysis_config,
        )

    @patch("src.backend.text_analysis.text_analyzer.LlmOpenAI")
    def test_analyze_with_json_schema(
        self,
        mock_llm_class,
        analyzer,
        sample_llm_config,
    ) -> None:
        """Test analyze() avec response_format_type='json_object'."""
        with patch(
            "src.backend.text_analysis.text_analyzer.short_hash",
            return_value="test_hash",
        ), patch(
            "src.backend.text_analysis.text_analyzer.get_cache_file_path",
        ) as mock_get_cache:
            mock_get_cache.return_value = "/tmp/cache.json"

            # Mock LLM response
            mock_llm_instance = Mock()
            mock_result = Mock()
            mock_result.model_dump.return_value = {
                "scorings": [
                    {
                        "intention_id": "intention1",
                        "score": 8,
                        "justification": "Test justification",
                    },
                ],
                "nom": "Dupont",
            }
            mock_llm_instance.call_llm_with_json_schema.return_value = mock_result
            mock_llm_class.return_value = mock_llm_instance

            # Test
            result = analyzer.analyze(
                locale="fr",
                llm_config=sample_llm_config,
                field_values={},
                text="Je m'appelle Dupont",
                read_from_cache=False,
            )

            # Vérifications
            assert KEY_ANALYSIS_RESULT in result
            assert KEY_PROMPT in result
            assert KEY_MARKDOWN_TABLE in result
            assert KEY_HIGHLIGHTED_TEXT_AND_FEATURES in result

            analysis_result = result[KEY_ANALYSIS_RESULT]
            assert FIELD_NAME_SCORINGS in analysis_result
            assert KEY_STATISTICS in analysis_result

    @patch("src.backend.text_analysis.text_analyzer.LlmOpenAI")
    def test_analyze_with_pydantic_model(self, mock_llm_class, analyzer) -> None:
        """Test analyze() avec response_format_type='pydantic_model'."""
        mock_llm_config = LlmConfig(
            id="test_config",
            llm="openai",
            model="gpt-4",
            response_format_type="pydantic_model",
            prompt_format="text",
            temperature=0.7,
        )

        with patch(
            "src.backend.text_analysis.text_analyzer.short_hash",
            return_value="test_hash",
        ), patch(
            "src.backend.text_analysis.text_analyzer.get_cache_file_path",
        ) as mock_get_cache:
            mock_get_cache.return_value = "/tmp/cache.json"

            mock_llm_instance = Mock()
            mock_result = Mock()
            mock_result.model_dump.return_value = {
                "scorings": [
                    {
                        "intention_id": "intention1",
                        "score": 5,
                        "justification": "Test",
                    },
                ],
                "nom": None,
            }
            mock_llm_instance.call_llm_with_pydantic_model.return_value = mock_result
            mock_llm_class.return_value = mock_llm_instance

            result = analyzer.analyze(
                locale="fr",
                llm_config=mock_llm_config,
                field_values={},
                text="Test text",
                read_from_cache=False,
            )

            assert KEY_ANALYSIS_RESULT in result
            mock_llm_instance.call_llm_with_pydantic_model.assert_called_once()

    @patch("src.backend.text_analysis.text_analyzer.short_hash")
    @patch("src.backend.text_analysis.text_analyzer.get_cache_file_path")
    def test_analyze_with_cache(
        self,
        mock_get_cache_path,
        mock_hash,
        analyzer,
        sample_llm_config,
    ) -> None:
        """Test analyze() avec read_from_cache=True."""
        # Mock hash
        mock_hash.return_value = "test_hash"

        # Créer un fichier de cache avec tous les champs nécessaires
        cache_data = {
            "scorings": [
                {
                    "intention_id": "intention1",
                    "score": 10,
                    "justification": "Cached result",
                },
            ],
            KEY_STATISTICS: {"Response time": "0.5s"},
            KEY_HASH_CODE: "test_hash",
            "nom": "Dupont",  # Ajouter le champ feature pour éviter KeyError dans build_html
        }

        cache_path = os.path.join(
            analyzer.runtime_directory,
            "cache",
            "cache_test_app_fr_test_hash.json",
        )
        mock_get_cache_path.return_value = cache_path
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)

        result = analyzer.analyze(
            locale="fr",
            llm_config=sample_llm_config,
            field_values={},
            text="Test text",
            read_from_cache=True,
        )

        assert KEY_ANALYSIS_RESULT in result
        analysis_result = result[KEY_ANALYSIS_RESULT]
        assert analysis_result[FIELD_NAME_SCORINGS][0]["score"] == 10

    @patch("src.backend.text_analysis.text_analyzer.short_hash")
    @patch("src.backend.text_analysis.text_analyzer.get_cache_file_path")
    def test_analyze_cache_missing_file(
        self,
        mock_get_cache_path,
        mock_hash,
        analyzer,
        sample_llm_config,
    ) -> None:
        """Test analyze() avec cache manquant (doit utiliser LLM)."""
        mock_hash.return_value = "test_hash"
        cache_path = os.path.join(
            analyzer.runtime_directory,
            "cache",
            "cache_test_app_fr_test_hash.json",
        )
        mock_get_cache_path.return_value = cache_path

        # Ne pas créer le fichier de cache

        with patch(
            "src.backend.text_analysis.text_analyzer.LlmOpenAI",
        ) as mock_llm_class:
            mock_llm_instance = Mock()
            mock_result = Mock()
            mock_result.model_dump.return_value = {"scorings": [], "nom": None}
            mock_llm_instance.call_llm_with_json_schema.return_value = mock_result
            mock_llm_class.return_value = mock_llm_instance

            analyzer.analyze(
                locale="fr",
                llm_config=sample_llm_config,
                field_values={},
                text="Test text",
                read_from_cache=True,  # Demande cache mais fichier n'existe pas
            )

            # Doit avoir appelé le LLM
            mock_llm_instance.call_llm_with_json_schema.assert_called_once()

    def test_analyze_unsupported_llm(self, analyzer) -> None:
        """Test que ValueError est levée pour un LLM non supporté."""
        # Créer un mock LlmConfig avec un llm invalide en bypassant la validation Pydantic
        mock_llm_config = Mock()
        mock_llm_config.id = "test_config"
        mock_llm_config.llm = "unsupported"
        mock_llm_config.model = "test"
        mock_llm_config.response_format_type = "json_object"
        mock_llm_config.prompt_format = "markdown"
        mock_llm_config.temperature = 0.7

        with pytest.raises(ValueError, match="Unsupported LLM"):
            analyzer._analyze(
                llm_config=mock_llm_config,
                field_values={},
                text="Test",
                read_from_cache=False,
            )

    @patch("src.backend.text_analysis.text_analyzer.LlmOllama")
    def test_analyze_with_ollama(self, mock_llm_class, analyzer) -> None:
        """Test avec LLM Ollama."""
        mock_llm_config = LlmConfig(
            id="test_config",
            llm="ollama",
            model="llama2",
            response_format_type="json_object",
            prompt_format="markdown",
            temperature=0.7,
        )

        # Mock pour éviter les problèmes d'initialisation
        with patch(
            "src.backend.text_analysis.text_analyzer.short_hash",
            return_value="test_hash",
        ), patch(
            "src.backend.text_analysis.text_analyzer.get_cache_file_path",
        ) as mock_get_cache:
            mock_get_cache.return_value = "/tmp/cache.json"

            mock_llm_instance = Mock()
            mock_result = Mock()
            mock_result.model_dump.return_value = {"scorings": [], "nom": None}
            mock_llm_instance.call_llm_with_json_schema.return_value = mock_result
            mock_llm_class.return_value = mock_llm_instance

            result = analyzer.analyze(
                locale="fr",
                llm_config=mock_llm_config,
                field_values={},
                text="Test",
                read_from_cache=False,
            )

            assert KEY_ANALYSIS_RESULT in result
            mock_llm_class.assert_called_once_with(mock_llm_config)

    @patch("src.backend.text_analysis.text_analyzer.LlmScaleway")
    def test_analyze_with_scaleway(self, mock_llm_class, analyzer) -> None:
        """Test avec LLM Scaleway."""
        mock_llm_config = LlmConfig(
            id="test_config",
            llm="scaleway",
            model="mistral-large",
            response_format_type="json_object",
            prompt_format="markdown",
            temperature=0.7,
        )

        # Mock pour éviter les problèmes d'initialisation
        with patch(
            "src.backend.text_analysis.text_analyzer.short_hash",
            return_value="test_hash",
        ), patch(
            "src.backend.text_analysis.text_analyzer.get_cache_file_path",
        ) as mock_get_cache:
            mock_get_cache.return_value = "/tmp/cache.json"

            mock_llm_instance = Mock()
            mock_result = Mock()
            mock_result.model_dump.return_value = {"scorings": [], "nom": None}
            mock_llm_instance.call_llm_with_json_schema.return_value = mock_result
            mock_llm_class.return_value = mock_llm_instance

            result = analyzer.analyze(
                locale="fr",
                llm_config=mock_llm_config,
                field_values={},
                text="Test",
                read_from_cache=False,
            )

            assert KEY_ANALYSIS_RESULT in result
            mock_llm_class.assert_called_once_with(mock_llm_config)

    @patch("src.backend.text_analysis.text_analyzer.LlmOpenAI")
    def test_analyze_adds_intention_other(
        self,
        mock_llm_class,
        analyzer,
        sample_llm_config,
    ) -> None:
        """Test que l'intention 'other' est ajoutée."""
        with patch(
            "src.backend.text_analysis.text_analyzer.short_hash",
            return_value="test_hash",
        ), patch(
            "src.backend.text_analysis.text_analyzer.get_cache_file_path",
        ) as mock_get_cache:
            mock_get_cache.return_value = "/tmp/cache.json"

            mock_llm_instance = Mock()
            mock_result = Mock()
            mock_result.model_dump.return_value = {
                "scorings": [
                    {
                        "intention_id": "intention1",
                        "score": 5,
                        "justification": "Test",
                    },
                ],
                "nom": None,
            }
            mock_llm_instance.call_llm_with_json_schema.return_value = mock_result
            mock_llm_class.return_value = mock_llm_instance

            result = analyzer.analyze(
                locale="fr",
                llm_config=sample_llm_config,
                field_values={},
                text="Test",
                read_from_cache=False,
            )

            analysis_result = result[KEY_ANALYSIS_RESULT]
            scorings = analysis_result[FIELD_NAME_SCORINGS]

            # Vérifier qu'il y a au moins 2 scorings (intention1 + other)
            assert len(scorings) >= 2

            # Trouver l'intention "other"
            other_scoring = next(
                (s for s in scorings if s.get("intention_id") == "other"),
                None,
            )
            assert other_scoring is not None
            assert other_scoring.get("intention_label") == "AUTRE"  # En français


class TestTextAnalyzerBuildPrompt:
    """Tests pour build_localizedsystem_prompt_template()."""

    @pytest.fixture()
    def analyzer(
        self,
        sample_case_model,
        sample_text_analysis_config,
        temp_runtime_directory,
    ):
        return TextAnalyzer(
            runtime_directory=temp_runtime_directory,
            app_id="test_app",
            locale="fr",
            case_model=sample_case_model,
            text_analysis_config=sample_text_analysis_config,
        )

    def test_build_prompt_markdown(self, analyzer, sample_llm_config) -> None:
        """Test construction du prompt en markdown."""
        prompt = analyzer.build_localizedsystem_prompt_template(sample_llm_config)

        assert len(prompt) > 0
        # Le prompt doit contenir des informations sur les intentions
        assert "intention" in prompt.lower() or "Intention" in prompt

    def test_build_prompt_text(self, analyzer) -> None:
        """Test construction du prompt en texte."""
        llm_config = LlmConfig(
            id="test",
            llm="openai",
            model="gpt-4",
            response_format_type="json_object",
            prompt_format="text",
            temperature=0.7,
        )

        prompt = analyzer.build_localizedsystem_prompt_template(llm_config)

        assert len(prompt) > 0
        assert "intention" in prompt.lower()

    def test_build_prompt_includes_intentions(
        self, analyzer, sample_llm_config
    ) -> None:
        """Test que le prompt inclut les intentions."""
        prompt = analyzer.build_localizedsystem_prompt_template(sample_llm_config)

        # Le prompt doit mentionner l'intention configurée
        assert "intention1" in prompt.lower() or "Intention 1" in prompt

    def test_build_prompt_includes_definitions(
        self, analyzer, sample_llm_config
    ) -> None:
        """Test que le prompt inclut les définitions."""
        prompt = analyzer.build_localizedsystem_prompt_template(sample_llm_config)

        # Le prompt doit mentionner les définitions
        assert "terme1" in prompt.lower() or "définition" in prompt.lower()
