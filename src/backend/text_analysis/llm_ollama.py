from __future__ import annotations

from typing import Type

import ollama
from pydantic import BaseModel

from src.backend.text_analysis.llm import Llm, LlmConfig


class LlmOllama(Llm):
    def __init__(self, llm_config: LlmConfig) -> None:
        super().__init__(llm_config)
        self.build_client(llm_config)

    def build_client(self, config) -> None:
        self.client = None

    def call_llm_with_json_schema(self,
                                  analysis_response_model: Type[BaseModel],
                                  system_prompt: str,
                                  text: str) -> BaseModel:
        # Using Ollama to generate a completion in JSON format
        response = ollama.chat(
            model=self.llm_config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            options={
                "temperature": self.llm_config.temperature,
                "format": "json"
            }
        )
        content = response["message"]["content"]
        if content is None:
            raise ValueError("The LLM response is empty or null.")

        # Remove first and last lines if first line contains "```json" and last line contains "```"
        if content.startswith("```json") and content.endswith("```"):
            content = content[8:-3].strip()
        
        return analysis_response_model.model_validate_json(content)

    def call_llm_with_pydantic_model(self,
                                     analysis_response_model: Type[BaseModel],
                                     system_prompt: str,
                                     text: str) -> BaseModel:
        # Ollama doesn't manage output in Pydantic format
        raise ValueError("Ollama doesn't manage structured output in Pydantic format")
