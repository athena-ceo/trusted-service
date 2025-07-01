from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

from src.backend.text_analysis.text_analysis_configuration import TextAnalysisConfiguration


# Important: Update TextAnalyzer.__init__ when adding a new subclass

class Llm(ABC):

    @abstractmethod
    def call_llm_with_json_schema(self,
                                  config: TextAnalysisConfiguration,
                                  analysis_response_model: Type[BaseModel],
                                  system_prompt: str,
                                  text: str) -> BaseModel:
        pass

    @abstractmethod
    def call_llm_with_pydantic_model(self,
                                     config: TextAnalysisConfiguration,
                                     analysis_response_model: Type[BaseModel],
                                     system_prompt: str,
                                     text: str) -> BaseModel:
        pass
