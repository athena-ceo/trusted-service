from typing import cast

from src.common.configuration import Configuration, load_configuration_from_workbook


class BackendConfiguration(Configuration):
    runtime_directory: str  # The directory where various app-specific runtime artefacts are stored, in particular the caching of text analysis.
    # It is relative to the directory from where the app is run
    decision_engine: str
    distribution_engine: str


def load_backend_configuration_from_workbook(filename: str) -> BackendConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="backend",
                                                           collections=[],
                                                           configuration_type=BackendConfiguration)
    return cast(BackendConfiguration, conf)
