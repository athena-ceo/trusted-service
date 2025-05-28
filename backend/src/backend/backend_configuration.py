from typing import cast

from common.src.configuration import Configuration, load_configuration_from_workbook


class BackendConfiguration(Configuration):
    decision_engine: str
    distribution_engine: str


def load_backend_configuration_from_workbook(filename: str) -> BackendConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="backend",
                                                           collections=[],
                                                           configuration_type=BackendConfiguration)
    return cast(BackendConfiguration, conf)
