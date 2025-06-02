from typing import cast, Literal

from src.common.configuration import Configuration, load_configuration_from_workbook


class FrontendConfiguration(Configuration):
    connection_to_api: Literal["http", "direct"]
    http_connection_url: str

def load_frontend_configuration_from_workbook(filename: str) -> FrontendConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="frontend",
                                                           collections=[],
                                                           configuration_type=FrontendConfiguration)
    return cast(FrontendConfiguration, conf)

# def get_localization(config: FrontendConfiguration) -> FrontendLocalization:
#        return FrontendLocalizationEn() if config.locale == "en" else FrontendLocalizationFr()
