import yaml

from src.backend.text_analysis.llm import LlmConfig
from pydantic import BaseModel


class ServerConfig(BaseModel):
    llm_configs: list[LlmConfig]

    @staticmethod
    def load_from_yaml_file(path: str) -> 'ServerConfig':
        with open(path, "r") as file:
            config_data = yaml.safe_load(file)

        return ServerConfig(**config_data)
