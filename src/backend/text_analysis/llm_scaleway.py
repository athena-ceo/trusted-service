from __future__ import annotations

import os
from typing import Type

from openai import OpenAI
from pydantic import BaseModel

from src.backend.text_analysis.llm import Llm
from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration


class LlmScaleway(Llm):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.build_client(config)

    def build_client(self, config) -> None:
        project_id = os.environ.get("SCW_PROJECT_ID")
        if not project_id:
            raise ValueError("SCW_PROJECT_ID environment variable is not set")
        
        api_key = os.environ.get("SCW_SECRET_KEY")
        if not api_key:
            raise ValueError("SCW_SECRET_KEY environment variable is not set")
        
        self.client = OpenAI(
            base_url=f"https://api.scaleway.ai/{project_id}/v1",
            api_key=api_key
        )

    def call_llm_with_json_schema(self,
                                  analysis_response_model: Type[BaseModel],
                                  system_prompt: str,
                                  text: str) -> BaseModel:
        # Using OpenAI API with Scaleway to generate a completion in JSON format
        response = self.client.chat.completions.parse(
            model=self.config.model,
            response_format={"type": "json_object"},
            messages=[
                { "role": "system", "content": system_prompt },
                { "role": "user", "content": text },
            ],
            temperature=self.config.temperature,
            top_p=0.9,
            presence_penalty=0,
        )

        content = response.choices[0].message.content
        return analysis_response_model.model_validate_json(content)

    def call_llm_with_pydantic_model(self,
                                     analysis_response_model: Type[BaseModel],
                                     system_prompt: str,
                                     text: str) -> BaseModel:
        # Scaleway's API doesn't manage output in Pydantic format
        raise ValueError("Scaleway's API doesn't manage structured output in Pydantic format")
