"""
Evaluate how strongly a piece of text expresses a set of “intentions”
using OpenAI Chat Completions, with all I/O validated by Pydantic.

Author: Francis Friedlander
Date: 2025-04-29

"""

from __future__ import annotations

import json
from typing import List, Type, Optional, Any, Callable

from pydantic import BaseModel, Field, create_model

from backend.src.rendering.html import build_html_highlighted_text_and_features
from backend.src.rendering.md import build_markdown_table_intentions
from backend.src.text_analysis.base_models import Feature, PREFIX_FRAGMENTS, FIELD_NAME_SCORINGS
from backend.src.text_analysis.llm import Llm
from backend.src.text_analysis.llm_openai import LlmOpenAI
from backend.src.text_analysis.text_analysis_configuration import TextAnalysisConfiguration, get_localization
from common.src.constants import KEY_HIGHLIGHTED_TEXT_AND_FEATURES, KEY_ANALYSIS_RESULT, KEY_MARKDOWN_TABLE


class ListOfTextFragments(BaseModel):
    list: List[str]


def create_analysis_models(config: TextAnalysisConfiguration, features: list[Feature]):
    localization = get_localization(config)

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
            field_definitions[f"{PREFIX_FRAGMENTS}{feature.id}"] = (
                Optional[ListOfTextFragments], Field(default=None,
                                                     description=localization.description_of_fragments_feature(
                                                         feature.description)))

    return create_model(
        "AnalysisResult",
        __base__=class_scorings_for_multiple_intentions,
        **field_definitions)


def build_system_prompt(config: TextAnalysisConfiguration, features: list[Feature],
                        analysis_response_model: Type[BaseModel]) -> str:
    localization = get_localization(config)

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
            lines.append(f"- {PREFIX_FRAGMENTS}{f.id}: {localization.description_of_fragments_feature(f.id)}")

    if config.definitions:
        lines.append(f"--------- Définitions  ---------")
        for definition in config.definitions:
            lines.append(f"- {definition.term}: {definition.definition}")

    if config.response_format_type == "json_object":
        lines.append("---------")
        lines.append(f"{localization.promptstring_return_only_json}:")
        schema: str = json.dumps(analysis_response_model.model_json_schema(), indent=2)
        lines.append(f"{schema}")

    system_prompt = "\n".join(lines)

    return system_prompt


class TextAnalyzer:
    def __init__(self, config: TextAnalysisConfiguration, features: list[Feature]):
        self.config: TextAnalysisConfiguration = config
        self.features: list[Feature] = features
        self.analysis_response_model: Type[BaseModel] = create_analysis_models(config, features)
        self.templated_system_prompt: str = build_system_prompt(self.config, self.features, self.analysis_response_model)
        self.llm: Llm = LlmOpenAI() if config.llm == "openai" else LlmOpenAI()

    def analyze(self, field_values: dict[str, Any], text: str) -> dict[str, str]:

        system_prompt = self.templated_system_prompt

        for k, v in field_values.items():
            system_prompt = system_prompt.replace("{" + k + "}", str(v))  # a copy, so no change of original prompt

        print("---------- begin system_prompt ----------")
        print(system_prompt)
        print("----------- end system_prompt -----------")

        # Calling LLM

        # read_from_cache = True

        if self.config.read_from_cache:
            with open(file="cache.json", mode="r", encoding="utf-8") as f:
                analysis_result = json.load(f)
        else:
            if self.config.response_format_type == "json_object":
                _analysis_result: BaseModel = self.llm.call_llm_with_json_schema(self.config,
                                                                                 self.analysis_response_model,
                                                                                 self.templated_system_prompt, text)
            else:
                _analysis_result: BaseModel = self.llm.call_llm_with_pydantic_model(self.config,
                                                                                    self.analysis_response_model,
                                                                                    self.templated_system_prompt, text)
            analysis_result: dict[str, Any] = _analysis_result.model_dump(mode="json")

            # save_to_cache = True
            if self.config.save_to_cache:
                with open(file="cache.json", mode="w", encoding="utf-8") as f:
                    json.dump(analysis_result, f, ensure_ascii=False)

        # Joining with collection of intentions
        for scoring in analysis_result[FIELD_NAME_SCORINGS]:
            matching_intentions = [intention for intention in self.config.intentions if
                                   intention.id == scoring["intention_id"]]
            matching_intention = matching_intentions[0] if matching_intentions else None
            scoring["intention_label"] = matching_intention.label if matching_intention else None

        analysis_result[FIELD_NAME_SCORINGS] = [scoring for scoring in analysis_result[FIELD_NAME_SCORINGS] if
                                                scoring["intention_label"] is not None]

        return analysis_result

    def analyze_and_render(self, field_values: dict[str, Any], text: str) -> dict[str, str]:

        analysis_result = self.analyze(field_values, text)

        analysis_result_and_rendering = {
            KEY_ANALYSIS_RESULT: analysis_result,  # json.dumps(analysis_result),
            KEY_MARKDOWN_TABLE: build_markdown_table_intentions(analysis_result),
            KEY_HIGHLIGHTED_TEXT_AND_FEATURES: build_html_highlighted_text_and_features(text, self.features,
                                                                                        analysis_result)
        }

        return analysis_result_and_rendering
