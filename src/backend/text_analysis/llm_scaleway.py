from __future__ import annotations

import os
from typing import TYPE_CHECKING

from openai import OpenAI
from pydantic_core import ValidationError as PydanticCoreValidationError

from src.backend.text_analysis.llm import Llm, LlmConfig

if TYPE_CHECKING:
    from pydantic import BaseModel


class LlmScaleway(Llm):
    def __init__(self, llm_config: LlmConfig) -> None:
        super().__init__(llm_config)
        self.build_client()

    def build_client(self) -> None:
        project_id = os.environ.get("SCW_PROJECT_ID")
        if not project_id:
            msg = "SCW_PROJECT_ID environment variable is not set"
            raise ValueError(msg)

        api_key = os.environ.get("SCW_SECRET_KEY")
        if not api_key:
            msg = "SCW_SECRET_KEY environment variable is not set"
            raise ValueError(msg)

        self.client = OpenAI(
            base_url=f"https://api.scaleway.ai/{project_id}/v1",
            api_key=api_key,
        )

    def call_llm_with_json_schema(
        self,
        analysis_response_model: type[BaseModel],
        system_prompt: str,
        text: str,
    ) -> BaseModel:
        # Using OpenAI API with Scaleway to generate a completion in JSON format
        response = self.client.chat.completions.parse(
            model=self.llm_config.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=self.llm_config.temperature,
            top_p=0.9,
            presence_penalty=0,
        )

        content = response.choices[0].message.content
        try:
            return analysis_response_model.model_validate_json(content)
        except (PydanticCoreValidationError, ValueError) as e:
            # Si la validation échoue, c'est que le LLM a retourné un format incorrect
            # On propage l'erreur pour qu'elle soit gérée par le mécanisme de retry/fallback
            msg = f"LLM returned invalid JSON format: {e!s}"
            raise ValueError(msg) from e

    def call_llm_with_pydantic_model(
        self,
        analysis_response_model: type[BaseModel],
        system_prompt: str,
        text: str,
    ) -> BaseModel:
        # Scaleway's API doesn't manage output in Pydantic format
        msg = "Scaleway's API doesn't manage structured output in Pydantic format"
        raise ValueError(
            msg,
        )
