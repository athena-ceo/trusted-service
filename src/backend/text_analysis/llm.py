from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel

# Important: Update TextAnalyzer.__init__ when adding a new subclass


class LlmConfig(BaseModel):
    id: str
    llm: Literal["openai", "ollama", "scaleway"]
    model: str
    response_format_type: Literal["json_object", "pydantic_model"]
    prompt_format: Literal["markdown", "text"]
    temperature: float


class Llm(ABC):
    def __init__(self, llm_config: LlmConfig) -> None:
        self.client = None  # To be defined in the subclass
        # self.text_analysis_config = text_analysis_config
        self.llm_config: LlmConfig = llm_config

    # @abstractmethod
    # def build_client(self, llm_config: LlmConfig) -> None:
    #     pass

    @abstractmethod
    def call_llm_with_json_schema(
        self,
        analysis_response_model: type[BaseModel],
        system_prompt: str,
        text: str,
    ) -> BaseModel:
        pass

    @abstractmethod
    def call_llm_with_pydantic_model(
        self,
        analysis_response_model: type[BaseModel],
        system_prompt: str,
        text: str,
    ) -> BaseModel:
        pass
