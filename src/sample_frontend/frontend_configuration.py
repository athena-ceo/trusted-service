from typing import cast

from src.common.configuration import Configuration, load_configuration_from_workbook
from ssample_frontend.src.frontend_localization import FrontendLocalization, FrontendLocalizationFr, FrontendLocalizationEn


class FrontendConfiguration(Configuration):
    pass


def load_frontend_configuration_from_workbook(filename: str) -> FrontendConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab=None,
                                                           collections=[],
                                                           configuration_type=FrontendConfiguration)
    return cast(FrontendConfiguration, conf)



def get_localization(config: FrontendConfiguration) -> FrontendLocalization:
        return FrontendLocalizationEn() if config.locale == "en" else FrontendLocalizationFr()