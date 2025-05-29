from __future__ import annotations

from typing import Type

import openai
from openai import beta
from pydantic import BaseModel

from src.backend.text_analysis.llm import Llm
from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration

from openai import BaseModel


class LlmOpenAI(Llm):

    def call_llm_with_json_schema(self,
                                  config: TextAnalysisConfiguration,
                                  analysis_response_model: Type[BaseModel],
                                  system_prompt: str,
                                  text: str) -> BaseModel:
        completion = openai.chat.completions.create(
            model=config.model,
            response_format={"type": "json_object"},
            temperature=config.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )

        content = completion.choices[0].message.content

        # print(type(analysis_response_model.model_validate_json(content)))

        return analysis_response_model.model_validate_json(content)

    def call_llm_with_pydantic_model(self,
                                     config: TextAnalysisConfiguration,
                                     analysis_response_model: Type[BaseModel],
                                     system_prompt: str,
                                     text: str) -> BaseModel:
        completion = beta.chat.completions.parse(
            model=config.model,
            response_format=analysis_response_model,
            temperature=config.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )

        content = completion.choices[0].message.content

        return analysis_response_model.model_validate_json(content)
