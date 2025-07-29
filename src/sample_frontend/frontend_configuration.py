from typing import cast, Literal

from src.common.configuration import Configuration, load_configuration_from_workbook, SupportedLocale


class FrontendConfiguration(Configuration):
    connection_to_api: Literal["direct", "rest"]
    sample_text: str

def load_frontend_configuration_from_workbook(filename: str, locale: SupportedLocale) -> FrontendConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="frontend",
                                                           collections=[],
                                                           configuration_type=FrontendConfiguration,
                                                           locale=locale)
    return cast(FrontendConfiguration, conf)