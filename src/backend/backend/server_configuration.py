import yaml
from pydantic import BaseModel

from src.backend.text_analysis.llm import LlmConfig


class ServerConfiguration(BaseModel):
    home_directory: str
    llm_configs: list[LlmConfig]

    @staticmethod
    def load_from_yaml_file(path: str) -> 'ServerConfiguration':
        with open(path, "r") as file:
            config_data = yaml.safe_load(file)

        return ServerConfiguration(**config_data)