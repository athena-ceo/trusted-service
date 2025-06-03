from typing import cast, Literal

from src.common.configuration import Configuration, load_configuration_from_workbook, SupportedLocale


class CommonConfiguration(Configuration):
    locale: SupportedLocale
    client_url: str
    rest_api_host: str
    rest_api_port: int


def load_common_configuration_from_workbook(filename: str) -> CommonConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="common",
                                                           collections=[],
                                                           configuration_type=CommonConfiguration,
                                                           locale="en")  # Not relevant, but needed as positional arg required
    return cast(CommonConfiguration, conf)