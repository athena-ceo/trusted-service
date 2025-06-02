from typing import cast

from pydantic import BaseModel

from src.common.configuration import Configuration, load_configuration_from_workbook


class EmailTemplate(BaseModel):
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

    email_templates: list[EmailTemplate]


def load_email_configuration_from_workbook(filename: str) -> DistributionEmailConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="email_configuration",
                                                           collections=[("email_templates", EmailTemplate)],
                                                           configuration_type=DistributionEmailConfiguration)

    email_configuration: DistributionEmailConfiguration = cast(DistributionEmailConfiguration, conf)

    # for email_template in email_configuration.email_templates:
    #     email_template.body = email_template.body.replace("\n", "<br>")

    return email_configuration
