from __future__ import annotations

from typing import Type

import ollama
from pydantic import BaseModel

from src.backend.text_analysis.llm import Llm
from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration


class LlmOllama(Llm):

    def call_llm_with_json_schema(self,
                                  config: TextAnalysisConfiguration,
                                  analysis_response_model: Type[BaseModel],
                                  system_prompt: str,
                                  text: str) -> BaseModel:
        # Using Ollama to generate a completion in JSON format
        response = ollama.chat(
            model=config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            options={
                "temperature": config.temperature,
                "format": "json"
            }
        )
        content = response["message"]["content"]
        return analysis_response_model.model_validate_json(content)

    def call_llm_with_pydantic_model(self,
                                     config: TextAnalysisConfiguration,
                                     analysis_response_model: Type[BaseModel],
                                     system_prompt: str,
                                     text: str) -> BaseModel:
        # Ollama doesn't manage output in Pydantic format
        return self.call_llm_with_json_schema(self, config, analysis_response_model, system_prompt, text)
