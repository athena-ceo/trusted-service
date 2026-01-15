from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import openai

from src.backend.text_analysis.llm import Llm, LlmConfig

if TYPE_CHECKING:
    from openai.types.chat.chat_completion import ChatCompletion
    from pydantic import BaseModel


class LlmOpenAI(Llm):
    def __init__(self, llm_config: LlmConfig) -> None:
        super().__init__(llm_config)
        self.build_client()

    def build_client(self) -> None:
        if "OPENAI_API_KEY" not in os.environ:
            msg = "OPENAI_API_KEY environment variable is not set"
            raise ValueError(msg)

        self.client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
        )

    def call_llm_with_json_schema(
        self,
        analysis_response_model: type[BaseModel],
        system_prompt: str,
        text: str,
    ) -> BaseModel:
        completion: ChatCompletion = self.client.chat.completions.create(
            # model=self.text_analysis_config.model,
            model=self.llm_config.model,
            response_format={"type": "json_object"},
            # temperature=self.text_analysis_config.temperature,
            temperature=self.llm_config.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )

        content: str | None = completion.choices[0].message.content

        if content is None:
            msg = "The LLM response is empty or null."
            raise ValueError(msg)
        # Ensure that content is a str, then encode it as bytes for model_validate_json
        if isinstance(content, str):
            return analysis_response_model.model_validate_json(content.encode("utf-8"))
        else:
            return analysis_response_model.model_validate_json(content)

    def call_llm_with_pydantic_model(
        self,
        analysis_response_model: type[BaseModel],
        system_prompt: str,
        text: str,
    ) -> BaseModel:

        # print("SYSTEM PROMPT:")
        # print(system_prompt)
        # print("USER PROMPT:")
        # print(text)
        # print("DONE")

        completion: Any = self.client.chat.completions.parse(
            # model=self.text_analysis_config.model,
            model=self.llm_config.model,
            response_format=analysis_response_model,
            # temperature=self.text_analysis_config.temperature,
            temperature=float(self.llm_config.temperature),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )

        content = completion.choices[0].message.content

        if content is None:
            msg = "The LLM response is empty or null."
            raise ValueError(msg)
        # Ensure that content is a str, then encode it as bytes for model_validate_json
        if isinstance(content, str):
            return analysis_response_model.model_validate_json(content.encode("utf-8"))
        else:
            return analysis_response_model.model_validate_json(content)
