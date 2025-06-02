from typing import cast, Literal

from src.common.configuration import Configuration, load_configuration_from_workbook


class CommonConfiguration(Configuration):
    # locale: str
    rest_api_host: str
    rest_api_port: int


def load_common_configuration_from_workbook(filename: str) -> CommonConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="common",
                                                           collections=[],
                                                           configuration_type=CommonConfiguration)
    return cast(CommonConfiguration, conf)