from typing import cast

from pydantic import BaseModel

from src.common.configuration import Configuration, load_configuration_from_workbook

# class ResponseTemplate(BaseModel):
#     id: str
#     subject: str
#     body: str

class DecisionODMConfiguration(Configuration):
    decision_service_url: str


def load_odm_configuration_from_workbook(filename: str) -> DecisionODMConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="odm",
                                                           collections=[],
                                                           configuration_type=DecisionODMConfiguration)
    # print(conf)
    return cast(DecisionODMConfiguration, conf)
