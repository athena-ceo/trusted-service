from typing import cast

from src.common.configuration import Configuration, load_configuration_from_workbook

class DecisionDroolsConfiguration(Configuration):
    drools_param: str


def load_drools_configuration_from_workbook(filename: str) -> DecisionDroolsConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="drools",
                                                           collections=[],
                                                           configuration_type=DecisionDroolsConfiguration)
    return cast(DecisionDroolsConfiguration, conf)
