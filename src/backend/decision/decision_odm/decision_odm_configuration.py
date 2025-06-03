from typing import cast

from pydantic import BaseModel

from src.common.configuration import Configuration, load_configuration_from_workbook, SupportedLocale


class DecisionODMConfiguration(Configuration):
    decision_service_url: str
    trace_rules: bool


def load_odm_configuration_from_workbook(filename: str, locale: SupportedLocale) -> DecisionODMConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="odm",
                                                           collections=[],
                                                           configuration_type=DecisionODMConfiguration,
                                                           locale=locale)
    return cast(DecisionODMConfiguration, conf)
