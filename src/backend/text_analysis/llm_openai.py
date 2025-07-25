from __future__ import annotations

import os
from typing import Type, Any

import openai
from openai import beta
from openai.types.chat.chat_completion import ChatCompletion
from pydantic import BaseModel

from src.backend.text_analysis.llm import Llm
from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration


class LlmOpenAI(Llm):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.build_client(config)

    def build_client(self, config) -> None:
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1"
        )

    def call_llm_with_json_schema(self,
                                  analysis_response_model: Type[BaseModel],
                                  system_prompt: str,
                                  text: str) -> BaseModel:
        completion: ChatCompletion = self.client.chat.completions.create(
            model=self.config.model,
            response_format={"type": "json_object"},
            temperature=self.config.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )

        content: str | None = completion.choices[0].message.content

        if content is None:
            raise ValueError("The LLM response is empty or null.")
        # Ensure that content is a str, then encode it as bytes for model_validate_json
        if isinstance(content, str):
            return analysis_response_model.model_validate_json(content.encode("utf-8"))
        else:
            return analysis_response_model.model_validate_json(content)

    def call_llm_with_pydantic_model(self,
                                     analysis_response_model: Type[BaseModel],
                                     system_prompt: str,
                                     text: str) -> BaseModel:
        completion: Any = self.client.chat.completions.parse(
            model=self.config.model,
            response_format=analysis_response_model,
            temperature=self.config.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )

        content = completion.choices[0].message.content

        if content is None:
            raise ValueError("The LLM response is empty or null.")
        # Ensure that content is a str, then encode it as bytes for model_validate_json
        if isinstance(content, str):
            return analysis_response_model.model_validate_json(content.encode("utf-8"))
        else:
            return analysis_response_model.model_validate_json(content)
