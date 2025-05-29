from typing import cast

from pydantic import BaseModel

from src.common.configuration import Configuration, load_configuration_from_workbook

class ResponseTemplate(BaseModel):
    id: str
    subject: str
    body: str

class DistributionEmailConfiguration(Configuration):
    hub_email_address: str
    agent_email_address: str
    case_field_email_address: str
    smtp_server: str
    password: str
    smtp_port: int

    email_templates: list[ResponseTemplate]


def load_email_configuration_from_workbook(filename: str) -> DistributionEmailConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="email_configuration",
                                                           collections=[("email_templates", ResponseTemplate)],
                                                           configuration_type=DistributionEmailConfiguration)
    # print(conf)
    return cast(DistributionEmailConfiguration, conf)
