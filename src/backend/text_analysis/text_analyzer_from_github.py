"""
Evaluate how strongly a piece of text expresses a set of “intentions”
using OpenAI (or Ollama with a specific model) Chat Completions, with all I/O validated by Pydantic.

Author: Francis Friedlander
Date: 2025-04-29

"""

from __future__ import annotations

import json
from typing import List, Type, Optional, Any

from pydantic import BaseModel, Field, create_model

from src.backend.rendering.html import build_html_highlighted_text_and_features
from src.backend.rendering.md import build_markdown_table_intentions
from src.backend.text_analysis.base_models import Feature, PREFIX_FRAGMENTS, FIELD_NAME_SCORINGS, Intention
from src.backend.text_analysis.llm import Llm
from src.backend.text_analysis.llm_openai import LlmOpenAI
from src.backend.text_analysis.llm_ollama import LlmOllama
from src.backend.text_analysis.llm_scaleway import LlmScaleway
from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration
from src.backend.text_analysis.text_analysis_localization import TextAnalysisLocalization, text_analysis_localizations
from src.common.case_model import CaseModel
from src.common.configuration import SupportedLocale
from src.common.constants import KEY_HIGHLIGHTED_TEXT_AND_FEATURES, KEY_ANALYSIS_RESULT, KEY_MARKDOWN_TABLE, KEY_PROMPT


class ListOfTextFragments(BaseModel):
    list: List[str]


def create_analysis_models(locale: SupportedLocale,
                           features: list[Feature]):
    localization: TextAnalysisLocalization = text_analysis_localizations[locale]  # Will fail here if language is not supported

    # class ScoringForOneIntention

    class_scoring_for_one_intention = create_model(
        "ScoringForOneIntention",
        __base__=BaseModel,
        intention_id=(str, Field(..., description=localization.docstring_scoring_for_one_intention_intention_id)),
        score=(int, Field(..., description=localization.docstring_scoring_for_one_intention_score)),
        justification=(str, Field(..., description=localization.docstring_scoring_for_one_intention_justification)),
    )

    class_scoring_for_one_intention.__doc__ = localization.docstring_scoring_for_one_intention

    # class ScoringForMultipleIntentions

    class_scorings_for_multiple_intentions = create_model(
        "ScoringForMultipleIntentions",
        __base__=BaseModel,
        scorings=(List[class_scoring_for_one_intention], Field(...)),
    )
    class_scorings_for_multiple_intentions.__doc__ = localization.docstring_scoring_for_multiple_intentions

    # Dynamic class AnalysisResult

    field_definitions = {}
    for feature in features:
        field_definitions[feature.id] = (
            Optional[feature.type], Field(default=None, description=feature.description))

        if feature.highlight_fragments:
            description = localization.promptstring_description_of_fragments_feature.format(description_of_feature=feature.description)
            # description=localization.description_of_fragments_feature(feature.description)))
            field_definitions[f"{PREFIX_FRAGMENTS}{feature.id}"] = Optional[ListOfTextFragments], Field(default=None, description=description)

    return create_model(
        "AnalysisResult",
        __base__=class_scorings_for_multiple_intentions,
        **field_definitions)


def build_system_prompt(config: TextAnalysisConfiguration,
                        locale: SupportedLocale,
                        features: list[Feature],
                        analysis_response_model: Type[BaseModel]) -> str:
    localization: TextAnalysisLocalization = text_analysis_localizations[locale]  # Will fail here if language is not supported

    lines = []

    if config.system_prompt_prefix:
        lines.append(config.system_prompt_prefix)

    if features:
        lines.append(localization.promptstring_perform_the_2_tasks_below)
        lines.append(f"--- {localization.promptstring_task} 1 ---")

    lines.append(localization.promptstring_instructions_intentions)
    lines.append(f"{localization.promptstring_list_of_intentions}:")
    for intention in config.intentions:
        lines.append(f"- {intention.id}: {intention.description}")

    if features:
        lines.append(f"--- {localization.promptstring_task} 2 ---")
        lines.append(f"{localization.promptstring_instructions_extract_features}:")
        for f in features:
            lines.append(f"- {f.id}: {f.description}")
            description = localization.promptstring_description_of_fragments_feature.format(description_of_feature=f.id)
            # lines.append(f"- {PREFIX_FRAGMENTS}{f.id}: {localization.description_of_fragments_feature(f.id)}")
            lines.append(f"- {PREFIX_FRAGMENTS}{f.id}: {description}")

    if config.definitions:
        lines.append(f"--------- Définitions  ---------")
        for definition in config.definitions:
            lines.append(f"- {definition.term}: {definition.definition}")

    if config.response_format_type == "json_object":
        lines.append("---------")
        lines.append(f"{localization.promptstring_return_only_json}:")
        schema: str = json.dumps(analysis_response_model.model_json_schema(), indent=2)
        lines.append(f"{schema}")

    md_line_break = "  "
    system_prompt = (md_line_break + "\n").join(lines)

    return system_prompt


class TextAnalyzer:
    def __init__(self,
                 case_model: CaseModel,
                 runtime_directory: str,
                 config: TextAnalysisConfiguration,
                 locale: SupportedLocale):

        self.case_model = case_model

        features: list[Feature] = []
        for case_field in case_model.case_fields:  ## TODO: Do that in the constructor of TextAnalyzer
            if case_field.extraction != "DO NOT EXTRACT":
                feature = Feature(id=case_field.id,
                                  label=case_field.label,
                                  type=case_field.type,
                                  description=case_field.description,
                                  highlight_fragments=case_field.extraction == "EXTRACT AND HIGHLIGHT")
                features.append(feature)
        self.features: list[Feature] = features

        self.runtime_directory: str = runtime_directory
        self.config2: TextAnalysisConfiguration = config
        self.analysis_response_model: Type[BaseModel] = create_analysis_models(locale, features)
        self.templated_system_prompt: str = build_system_prompt(self.config2, locale, self.features, self.analysis_response_model)
        self.localization: TextAnalysisLocalization = text_analysis_localizations[locale]  # Will fail here if language is not supported

        if config.llm == "openai":
            self.llm: Llm = LlmOpenAI(config)
        elif config.llm == "ollama":
            self.llm: Llm = LlmOllama(config)
        elif config.llm == "scaleway":
            self.llm: Llm = LlmScaleway(config)
        else:
            raise ValueError(f"Unsupported LLM: {config.llm}")


    def _analyze(self, field_values: dict[str, Any], text: str) -> tuple[str, dict[str, str]]:

        system_prompt = self.templated_system_prompt
        for k, v in field_values.items():
            system_prompt = system_prompt.replace("{" + k + "}", str(v))  # a copy, so no change of original prompt

        # Calling LLM

        cache_filename = self.runtime_directory + "/cache.json"

        if self.config2.read_from_cache:
            with open(file=cache_filename, mode="r", encoding="utf-8") as f:
                analysis_result = json.load(f)
        else:
            if self.config2.response_format_type == "json_object":
                _analysis_result: BaseModel = self.llm.call_llm_with_json_schema(self.analysis_response_model, system_prompt, text)
            else:
                _analysis_result: BaseModel = self.llm.call_llm_with_pydantic_model(self.analysis_response_model, system_prompt, text)
            analysis_result: dict[str, Any] = _analysis_result.model_dump(mode="json")

            # save_to_cache = True
            if self.config2.save_to_cache:
                with open(file=cache_filename, mode="w", encoding="utf-8") as f:
                    json.dump(analysis_result, f, ensure_ascii=False)

        # Joining with collection of intentions
        for scoring in analysis_result[FIELD_NAME_SCORINGS]:
            scoring: dict[int, str]

            matching_intentions = [intention for intention in self.config2.intentions if intention.id == scoring.get("intention_id")]
            if matching_intentions:
                matching_intention: Intention = matching_intentions[0]
                scoring["intention_label"] = matching_intention.label
                scoring["intention_fields"] = [case_field.id for case_field in self.case_model.case_fields if matching_intention.id in case_field.intention_ids]

        analysis_result[FIELD_NAME_SCORINGS] = [scoring for scoring in analysis_result[FIELD_NAME_SCORINGS] if
                                                scoring.get("intention_label") is not None]

        intention_other = Intention(id="other", label=self.localization.label_intention_other, description="Fallback")

        dict_other: dict[str, Any] = {
            "intention_id": intention_other.id,
            "score": 1,
            "justification": intention_other.description,
            "intention_label": intention_other.label,
            "intention_fields": [
            ]
        }

        analysis_result[FIELD_NAME_SCORINGS].append(dict_other)

        return system_prompt, analysis_result

    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, str]:

        system_prompt, analysis_result = self._analyze(field_values, text)

        analysis_result_and_rendering = {
            KEY_ANALYSIS_RESULT: analysis_result,  # json.dumps(analysis_result),
            KEY_PROMPT: system_prompt,
            KEY_MARKDOWN_TABLE: build_markdown_table_intentions(analysis_result),
            KEY_HIGHLIGHTED_TEXT_AND_FEATURES: build_html_highlighted_text_and_features(text, self.features, analysis_result)
        }

        return analysis_result_and_rendering