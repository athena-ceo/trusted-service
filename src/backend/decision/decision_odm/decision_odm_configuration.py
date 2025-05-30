from typing import cast

from pydantic import BaseModel

from src.common.configuration import Configuration, load_configuration_from_workbook

class DecisionODMConfiguration(Configuration):
    decision_service_url: str
    trace_rules: bool


def load_odm_configuration_from_workbook(filename: str) -> DecisionODMConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="odm",
                                                           collections=[],
                                                           configuration_type=DecisionODMConfiguration)
    return cast(DecisionODMConfiguration, conf)
