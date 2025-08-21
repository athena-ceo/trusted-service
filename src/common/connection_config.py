import yaml
from pydantic import BaseModel


class ConnectionConfig(BaseModel):
    client_url: str  # HttpUrl
    rest_api_host: str
    rest_api_port: int

    @staticmethod
    def load_from_yaml_file(path: str) -> 'ConnectionConfig':
        with open(path, "r") as file:
            config_data = yaml.safe_load(file)

        return ConnectionConfig(**config_data)
