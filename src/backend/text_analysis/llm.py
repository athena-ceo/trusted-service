from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel


# Important: Update TextAnalyzer.__init__ when adding a new subclass

class Llm(ABC):
    def __init__(self, config) -> None:
        self.client = None # To be defined in the subclass
        self.config = config

    @abstractmethod
    def build_client(self, config) -> None:
        pass

    @abstractmethod
    def call_llm_with_json_schema(self,
                                  analysis_response_model: Type[BaseModel],
                                  system_prompt: str,
                                  text: str) -> BaseModel:
        pass

    @abstractmethod
    def call_llm_with_pydantic_model(self,
                                     analysis_response_model: Type[BaseModel],
                                     system_prompt: str,
                                     text: str) -> BaseModel:
        pass
