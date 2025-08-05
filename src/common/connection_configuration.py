import yaml
from pydantic import BaseModel


class ConnectionConfiguration(BaseModel):
    client_url: str  # HttpUrl
    rest_api_host: str
    rest_api_port: int

    @staticmethod
    def load_from_yaml_file(path: str) -> 'ConnectionConfiguration':
        with open(path, "r") as file:
            config_data = yaml.safe_load(file)

        return ConnectionConfiguration(**config_data)
