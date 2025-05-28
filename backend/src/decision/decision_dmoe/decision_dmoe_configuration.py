from typing import cast

from common.src.configuration import Configuration, load_configuration_from_workbook

class DecisionDMOEConfiguration(Configuration):
    dmoe_param: str


def load_dmoe_configuration_from_workbook(filename: str) -> DecisionDMOEConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="dmoe",
                                                           collections=[],
                                                           configuration_type=DecisionDMOEConfiguration)
    # print(conf)
    return cast(DecisionDMOEConfiguration, conf)
