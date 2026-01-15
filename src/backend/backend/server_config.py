from __future__ import annotations

import yaml
from pydantic import BaseModel

from src.backend.text_analysis.llm import LlmConfig


class ServerConfig(BaseModel):
    llm_configs: list[LlmConfig]

    @staticmethod
    def load_from_yaml_file(path: str) -> ServerConfig:
        with open(path) as file:
            config_data = yaml.safe_load(file)

        return ServerConfig(**config_data)
