"""
Fixtures communes pour tous les tests
"""
import pytest
import tempfile
import os
from unittest.mock import Mock

from src.common.case_model import CaseModel, CaseField
from src.backend.text_analysis.text_analyzer import TextAnalysisConfig
from src.backend.text_analysis.base_models import Intention, Definition
from src.backend.text_analysis.llm import LlmConfig
from src.common.config import SupportedLocale


@pytest.fixture
def sample_case_field():
    """Fixture pour un CaseField de test"""
    return CaseField(
        id="nom",
        type="str",
        label="Nom",
        mandatory=True,
        help="Nom de famille",
        format="",
        allowed_values_list_name="",
        allowed_values=[],
        default_value=None,
        scope="REQUESTER",
        show_in_ui=True,
        intention_ids=["intention1"],
        description="Nom de famille",
        extraction="EXTRACT",
        send_to_decision_engine=True
    )


@pytest.fixture
def sample_case_model(sample_case_field):
    """Fixture pour un CaseModel de test"""
    return CaseModel(case_fields=[sample_case_field])


@pytest.fixture
def sample_text_analysis_config():
    """Fixture pour un TextAnalysisConfig de test"""
    return TextAnalysisConfig(
        system_prompt_prefix="Analyse le texte suivant",
        definitions=[
            Definition(term="terme1", definition="Définition du terme 1")
        ],
        intentions=[
            Intention(
                id="intention1",
                label="Intention 1",
                description="Description intention 1"
            )
        ]
    )


@pytest.fixture
def sample_llm_config():
    """Fixture pour un LlmConfig de test"""
    return LlmConfig(
        id="test_config",
        llm="openai",
        model="gpt-4",
        response_format_type="json_object",
        prompt_format="markdown",
        temperature=0.7
    )


@pytest.fixture
def temp_runtime_directory():
    """Fixture pour un répertoire runtime temporaire"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

