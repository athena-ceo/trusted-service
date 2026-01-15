from __future__ import annotations

import os
import smtplib
from typing import cast

from pydantic import BaseModel

from src.common.config import Config, SupportedLocale, load_config_from_workbook


class EmailTemplate(BaseModel):
    id: str
    subject: str
    body: str


class DistributionEmailConfig(Config):
    hub_email_address: str
    agent_email_address: str
    case_field_email_address: str
    smtp_server: str
    smtp_username: str | None = (
        None  # Username for SMTP authentication (optional for backwards compatibility)
    )
    password_key: str | None = (
        None  # Name of environment variable containing SMTP password (e.g., EMAIL_PASSWORD_AISA)
    )
    password: str | None = None  # Password loaded from environment variable at startup
    smtp_port: int
    send_email: bool

    email_templates: list[EmailTemplate]


def load_email_config_from_workbook(
    filename: str,
    locale: SupportedLocale,
) -> DistributionEmailConfig:
    conf: Config = load_config_from_workbook(
        filename=filename,
        main_tab="email_config",
        collections=[("email_templates", EmailTemplate)],
        config_type=DistributionEmailConfig,
        locale=locale,
    )

    email_config: DistributionEmailConfig = cast(DistributionEmailConfig, conf)

    return email_config


def validate_email_config_at_startup(
    email_config: DistributionEmailConfig,
    app_id: str | None = None,
) -> None:
    """Validates email configuration at server startup.
    Loads password from environment variable specified in password_key.
    Tests SMTP server connection.

    Args:
    ----
        email_config: Email configuration to validate
        app_id: Application ID (for logging purposes)

    Raises:
    ------
        EnvironmentError: If environment variable or SMTP connection fails

    """
    if not email_config.send_email:
        # Email is not enabled, no need to validate password
        return

    if not email_config.password_key:
        app_context = f" (app: {app_id})" if app_id else ""
        msg = (
            f"Missing required 'password_key' in email_config workbook{app_context}. "
            "Please define the environment variable name to use for SMTP password."
        )
        raise RuntimeError(
            msg,
        )

    # Load password from environment variable using the key specified in config
    email_password = os.getenv(email_config.password_key)

    if not email_password:
        app_context = f" (app: {app_id})" if app_id else ""
        error_msg = (
            f"❌ CRITICAL ERROR: Environment variable '{email_config.password_key}' is not defined{app_context}.\n"
            "   Email sending is enabled (send_email=True) but SMTP password is missing.\n"
            "   \n"
            "   REQUIRED ACTIONS:\n"
            f"   1. Set environment variable: export {email_config.password_key}='your_password'\n"
            "   2. Restart the server\n"
            "   \n"
            "   Server will now stop."
        )
        raise RuntimeError(error_msg)

    # Assign password to configuration
    email_config.password = email_password
    if app_id:
        pass
    else:
        pass

    # Test SMTP server connection
    _test_smtp_connection(email_config, app_id)


def _test_smtp_connection(
    email_config: DistributionEmailConfig,
    app_id: str | None = None,
) -> None:
    """Tests SMTP server connection with provided credentials.
    Stops the server if connection fails.

    Args:
    ----
        email_config: Email configuration with SMTP details
        app_id: Application ID (for logging purposes)

    """
    try:
        app_context = f" (app: {app_id})" if app_id else ""

        # Determine username to use
        smtp_username = (
            email_config.smtp_username
            if email_config.smtp_username
            else email_config.hub_email_address
        )

        # Attempt connection
        with smtplib.SMTP(
            email_config.smtp_server,
            email_config.smtp_port,
            timeout=10,
        ) as server:
            server.set_debuglevel(0)
            server.starttls()
            server.login(smtp_username, email_config.password)

    except smtplib.SMTPAuthenticationError as e:
        app_context = f" (app: {app_id})" if app_id else ""
        error_msg = (
            f"❌ CRITICAL ERROR: SMTP authentication failed{app_context}.\n"
            f"   Server: {email_config.smtp_server}:{email_config.smtp_port}\n"
            f"   Username: {smtp_username}\n"
            f"   \n"
            "   Please check:\n"
            "   1. SMTP username (smtp_username in workbook)\n"
            f"   2. Password ({email_config.password_key} environment variable)\n"
            "   3. SMTP server parameters (smtp_server, smtp_port)\n"
            f"   \n"
            f"   Error details: {e}\n"
            "   \n"
            "   Server will now stop."
        )
        raise RuntimeError(error_msg)

    except (smtplib.SMTPException, OSError) as e:
        app_context = f" (app: {app_id})" if app_id else ""
        error_msg = (
            f"❌ CRITICAL ERROR: Cannot connect to SMTP server{app_context}.\n"
            f"   Server: {email_config.smtp_server}:{email_config.smtp_port}\n"
            f"   \n"
            "   Please check:\n"
            "   1. SMTP server is accessible\n"
            "   2. SMTP port is correct\n"
            "   3. Network connection is working\n"
            f"   \n"
            f"   Error details: {e}\n"
            "   \n"
            "   Server will now stop."
        )
        raise RuntimeError(error_msg)

    except Exception as e:
        app_context = f" (app: {app_id})" if app_id else ""
        error_msg = (
            f"❌ CRITICAL ERROR: Unexpected error occurred during SMTP test{app_context}.\n"
            f"   Server: {email_config.smtp_server}:{email_config.smtp_port}\n"
            f"   \n"
            f"   Error details: {e}\n"
            "   \n"
            "   Server will now stop."
        )
        raise RuntimeError(error_msg)
