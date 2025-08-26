"""
Evaluate how strongly a piece of text expresses a set of “intentions”
using OpenAI (or Ollama with a specific model) Chat Completions, with all I/O validated by Pydantic.

Author: Francis Friedlander
Date: 2025-04-29

"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import List, Type, Optional, Any, cast

from pydantic import BaseModel, Field, create_model

from src.backend.backend.paths import get_cache_file_path
from src.backend.rendering.html import build_html_highlighted_text_and_features
from src.backend.rendering.md import build_markdown_table_intentions, build_markdown_table
from src.backend.text_analysis.base_models import Feature, PREFIX_FRAGMENTS, FIELD_NAME_SCORINGS, Intention, Definition
from src.backend.text_analysis.llm import Llm, LlmConfig
from src.backend.text_analysis.llm_ollama import LlmOllama
from src.backend.text_analysis.llm_openai import LlmOpenAI
from src.backend.text_analysis.llm_scaleway import LlmScaleway
from src.backend.text_analysis.text_analysis_localization import TextAnalysisLocalization, text_analysis_localizations
from src.common.case_model import CaseModel
from src.common.config import SupportedLocale, Config, load_config_from_workbook
from src.common.constants import KEY_HIGHLIGHTED_TEXT_AND_FEATURES, KEY_ANALYSIS_RESULT, KEY_MARKDOWN_TABLE, KEY_PROMPT
from src.common.logging import print_red


class TextAnalysisConfig(Config):
    system_prompt_prefix: str
    definitions: list[Definition]
    intentions: list[Intention]


def load_text_analysis_config_from_workbook(filename: str, locale: SupportedLocale) -> TextAnalysisConfig:
    conf: Config = load_config_from_workbook(filename=filename,
                                             main_tab="text_analysis",
                                             collections=[("definitions", Definition), ("intentions", Intention)],
                                             config_type=TextAnalysisConfig,
                                             locale=locale)
    return cast(TextAnalysisConfig, conf)


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
            field_definitions[f"{PREFIX_FRAGMENTS}{feature.id}"] = Optional[ListOfTextFragments], Field(default=None, description=description)

    return create_model(
        "AnalysisResult",
        __base__=class_scorings_for_multiple_intentions,
        **field_definitions)


class TextAnalyzer:
    def __init__(self, runtime_directory: str, app_id: str, locale: SupportedLocale,  # llm_config: LlmConfig,
                 case_model: CaseModel, text_analysis_config: TextAnalysisConfig):

        start_init_datetime = datetime.now()

        self.runtime_directory = runtime_directory
        self.app_id = app_id
        self.locale = locale
        self.text_analysis_config = text_analysis_config  # TODO - READ HERE

        self.case_model: CaseModel = case_model

        features: list[Feature] = []
        for case_field in self.case_model.case_fields:
            if case_field.extraction != "DO NOT EXTRACT":
                feature = Feature(id=case_field.id,
                                  label=case_field.label,
                                  type=case_field.type,
                                  description=case_field.description,
                                  highlight_fragments=case_field.extraction == "EXTRACT AND HIGHLIGHT")
                features.append(feature)
        self.features: list[Feature] = features

        self.analysis_response_model: Type[BaseModel] = create_analysis_models(self.locale, features)

        self.localization: TextAnalysisLocalization = text_analysis_localizations[self.locale]  # Will fail here if language is not supported

        end_init_datetime = datetime.now()
        time_difference: timedelta = end_init_datetime - start_init_datetime
        seconds: float = time_difference.total_seconds()
        print(f"end_init_datetime - start_init_datetime: {seconds:.2f}s")

    def build_localizedsystem_prompt_template(self, llm_config: LlmConfig) -> str:
        """
        :return: The localized system prompt template with placeholders to be replaced with actual case fiels values 
        """

        text_analysis_config: TextAnalysisConfig = self.text_analysis_config
        features: list[Feature] = self.features

        localization: TextAnalysisLocalization = text_analysis_localizations[self.locale]  # Will fail here if language is not supported - b

        md_line_break = "  \n"

        lines: list[str] = []

        # Initial part

        if llm_config.prompt_format == "markdown":
            lines.append(localization.promptstring_prompt_is_markdown)
            lines.append("")

        if text_analysis_config.system_prompt_prefix:
            lines.append(text_analysis_config.system_prompt_prefix)
            lines.append("")

        if features:
            lines.append(localization.promptstring_perform_the_2_tasks_below)
            lines.append(f"## {localization.promptstring_task} 1")

        lines.append(localization.promptstring_instructions_intentions)
        lines.append(f"### {localization.promptstring_list_of_intentions}:")

        # Append a md_line_break to each string
        lines = [line + md_line_break for line in lines]
        system_prompt = "".join(lines)

        # List of intents

        rows = text_analysis_config.intentions
        column_names = [localization.promptstring_intent_id, localization.promptstring_intent_description]
        lambda1 = lambda intent: intent.id
        lambda2 = lambda intent: intent.description

        if llm_config.prompt_format == "markdown":
            system_prompt += build_markdown_table(rows, column_names, [lambda1, lambda2])
            system_prompt += md_line_break

        else:
            for definition in rows:
                system_prompt += f"- {lambda1(definition)}: {lambda2(definition)}{md_line_break}"

        # Features to extract

        if features:
            system_prompt += f"## {localization.promptstring_task} 2{md_line_break}"
            system_prompt += f"{localization.promptstring_instructions_extract_features}:{md_line_break}"

            rows: list[tuple[str, str]] = []
            for f in features:
                if llm_config.prompt_format == "markdown":
                    rows.append((f.id, f.description))
                else:
                    system_prompt += f"- {f.id}: {f.description}{md_line_break}"

                # TODO: check in the case model that extraction == "EXTRACT AND HIGHLIGHT" (copy this in the feature object)
                # TODO; Rename description_of_feature in *feature_id
                description_fragments = localization.promptstring_description_of_fragments_feature.format(description_of_feature=f.id)
                if llm_config.prompt_format == "markdown":
                    rows.append((PREFIX_FRAGMENTS + f.id, description_fragments))
                else:
                    system_prompt += f"- {PREFIX_FRAGMENTS}{f.id}: {description_fragments}{md_line_break}"

            if llm_config.prompt_format == "markdown":
                system_prompt += build_markdown_table(
                    rows=rows,
                    column_names=["Feature", "Description"],
                    producers=[lambda row: row[0], lambda row: row[1]])
                system_prompt += md_line_break

        if text_analysis_config.definitions:
            system_prompt += f"## {localization.promptstring_definitions}{md_line_break}"

            rows = text_analysis_config.definitions
            column_names = [localization.promptstring_term, localization.promptstring_definition]
            lambda1 = lambda definition: definition.term
            lambda2 = lambda definition: definition.definition

            if llm_config.prompt_format == "markdown":
                system_prompt += build_markdown_table(rows, column_names, [lambda1, lambda2])
                system_prompt += md_line_break

            else:
                for definition in rows:
                    system_prompt += f"- {lambda1(definition)}: {lambda2(definition)}{md_line_break}"
                system_prompt += f"---------{md_line_break}"

        # if text_analysis_config.response_format_type == "json_object":
        if llm_config.response_format_type == "json_object":
            system_prompt += f"{localization.promptstring_return_only_json}:{md_line_break}"
            schema: str = json.dumps(self.analysis_response_model.model_json_schema(), indent=2)
            system_prompt += f"```{schema}```"

        return system_prompt

    def _analyze(self, llm_config: LlmConfig, field_values: dict[str, Any], text: str, read_from_cache: bool) -> tuple[str, dict[str, str]]:

        # TODO: Save the system_prompt in cache and move down the lines that follow under else:  # read_from_cache

        localized_system_prompt_template: str = self.build_localizedsystem_prompt_template(llm_config)
        system_prompt = localized_system_prompt_template.format(**field_values)

        # Calling LLM

        # cache_filename = get_cache_file_path(self.runtime_directory, self.app_id, self.locale, system_prompt, text)
        cache_filename = get_cache_file_path(self.runtime_directory, self.app_id, self.locale)

        if read_from_cache and not os.path.exists(cache_filename):
            print_red(f"File {cache_filename} does not exist")
            read_from_cache = False

        if read_from_cache:
            with open(file=cache_filename, mode="r", encoding="utf-8") as f:
                analysis_result = json.load(f)

        else:

            before = datetime.now()

            if llm_config.llm == "openai":
                llm: Llm = LlmOpenAI(llm_config)
            elif llm_config.llm == "ollama":
                llm: Llm = LlmOllama(llm_config)
            elif llm_config.llm == "scaleway":
                llm: Llm = LlmScaleway(llm_config)
            else:
                raise ValueError(f"Unsupported LLM: {llm_config.llm}")

            if llm_config.response_format_type == "json_object":
                _analysis_result: BaseModel = llm.call_llm_with_json_schema(self.analysis_response_model, system_prompt, text)
            else:
                _analysis_result: BaseModel = llm.call_llm_with_pydantic_model(self.analysis_response_model, system_prompt, text)

            time_difference: timedelta = datetime.now() - before

            seconds: float = time_difference.total_seconds()

            print(f"{seconds:.2f}s")

            analysis_result: dict[str, Any] = _analysis_result.model_dump(mode="json")

        # Joining with collection of intentions
        # intention_id => intention_label, intention_fields
        for scoring in analysis_result[FIELD_NAME_SCORINGS]:
            scoring: dict[int, str]

            matching_intentions = [intention for intention in self.text_analysis_config.intentions if intention.id == scoring.get("intention_id")]
            if matching_intentions:
                matching_intention: Intention = matching_intentions[0]
                scoring["intention_label"] = matching_intention.label
                scoring["intention_fields"] = [case_field.id for case_field in self.case_model.case_fields if matching_intention.id in case_field.intention_ids]

        analysis_result[FIELD_NAME_SCORINGS] = [scoring for scoring in analysis_result[FIELD_NAME_SCORINGS] if
                                                scoring.get("intention_label") is not None]

        if not read_from_cache:
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

    def analyze(self, llm_config: LlmConfig, field_values: dict[str, Any], text: str, read_from_cache: bool) -> dict[str, str]:

        system_prompt, analysis_result = self._analyze(llm_config, field_values, text, read_from_cache)

        analysis_result_and_rendering = {
            KEY_ANALYSIS_RESULT: analysis_result,  # json.dumps(analysis_result),
            KEY_PROMPT: system_prompt,
            KEY_MARKDOWN_TABLE: build_markdown_table_intentions(analysis_result),
            KEY_HIGHLIGHTED_TEXT_AND_FEATURES: build_html_highlighted_text_and_features(text, self.features, analysis_result)
        }

        return analysis_result_and_rendering
