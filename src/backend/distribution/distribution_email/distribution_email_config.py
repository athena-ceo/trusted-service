from typing import cast

from pydantic import BaseModel

from src.common.config import Config, load_config_from_workbook, SupportedLocale


class EmailTemplate(BaseModel):
    id: str
    subject: str
    body: str


class DistributionEmailConfig(Config):
    hub_email_address: str
    agent_email_address: str
    case_field_email_address: str
    smtp_server: str
    smtp_username: str | None = None  # Username pour l'authentification SMTP (optionnel pour rétrocompatibilité)
    password: str
    smtp_port: int
    send_email: bool

    email_templates: list[EmailTemplate]


def load_email_config_from_workbook(filename: str, locale: SupportedLocale) -> DistributionEmailConfig:
    conf: Config = load_config_from_workbook(filename=filename,
                                             main_tab="email_config",
                                             collections=[("email_templates", EmailTemplate)],
                                             config_type=DistributionEmailConfig,
                                             locale=locale)

    email_config: DistributionEmailConfig = cast(DistributionEmailConfig, conf)

    return email_config
