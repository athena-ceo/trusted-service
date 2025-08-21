from typing import cast

from src.common.config import Config, load_config_from_workbook

class DecisionDroolsConfig(Config):
    drools_param: str


def load_drools_config_from_workbook(filename: str) -> DecisionDroolsConfig:
    conf: Config = load_config_from_workbook(filename=filename,
                                             main_tab="drools",
                                             collections=[],
                                             config_type=DecisionDroolsConfig)
    return cast(DecisionDroolsConfig, conf)
