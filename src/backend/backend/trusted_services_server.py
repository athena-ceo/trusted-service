from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.backend.backend.app import App
from src.common.logging import print_red, print_yellow
from src.common.server_api import (
    CaseHandlingDetailedResponse,
    CaseHandlingRequest,
    ServerApi,
)

if TYPE_CHECKING:
    from src.common.case_model import CaseModel
    from src.common.config import SupportedLocale


class AppValidator:
    """Validates applications during server initialization and reload.
    Supports strict and lenient validation modes.
    """

    def __init__(self, validation_mode: str = "strict") -> None:
        """Initialize validator with specified mode.

        Args:
        ----
            validation_mode: "strict" (fail on error) or "lenient" (log warnings, continue)

        """
        self.validation_mode = validation_mode
        self.validation_errors: list[tuple[str, str]] = []  # (app_id, error_message)

    def validate_apps(self, apps: dict[str, App]) -> None:
        """Validates all loaded applications.
        Performs email configuration validation for apps with email distribution enabled.

        Args:
        ----
            apps: Dictionary of app_id -> App instances

        Raises:
        ------
            SystemExit: If strict mode and validation fails

        """
        self.validation_errors.clear()

        for app_id, app in apps.items():
            self._validate_app(app_id, app)

        # Handle validation results based on mode
        if self.validation_errors:
            if self.validation_mode == "strict":
                self._handle_strict_errors()
            else:  # lenient
                self._handle_lenient_errors()
        else:
            pass

    def _validate_app(self, app_id: str, app: App) -> None:
        """Validates a single application.

        Args:
        ----
            app_id: Application ID
            app: App instance to validate

        """
        # Validate email configuration for all locales
        for locale, localized_app in app.localized_apps.items():
            if (
                hasattr(localized_app, "case_handling_distribution_engine")
                and localized_app.case_handling_distribution_engine is not None
            ):
                # Email distribution is configured
                if hasattr(
                    localized_app.case_handling_distribution_engine,
                    "email_config",
                ):
                    try:
                        from src.backend.distribution.distribution_email.distribution_email_config import (
                            validate_email_config_at_startup,
                        )

                        email_config = (
                            localized_app.case_handling_distribution_engine.email_config
                        )
                        validate_email_config_at_startup(email_config, app_id)
                    except Exception as e:
                        error_msg = f"Email configuration validation error (locale: {locale}): {e!s}"
                        self.validation_errors.append((app_id, error_msg))

    def _handle_strict_errors(self) -> None:
        """Handles validation errors in strict mode (stop server)."""
        error_msg = (
            f"❌ CRITICAL ERROR: Validation failed for {len(self.validation_errors)} application(s).\n"
            "   Running in STRICT mode - server will not start.\n\n"
        )
        for app_id, error in self.validation_errors:
            error_msg += f"   • {app_id}: {error}\n"
        error_msg += "\n   To continue with warnings, use: python launcher_api.py ./runtime --lenient"

        print_red(error_msg)
        sys.exit(1)

    def _handle_lenient_errors(self) -> None:
        """Handles validation errors in lenient mode (log warnings, continue)."""
        warning_msg = (
            f"⚠️  WARNING: Validation issues found in {len(self.validation_errors)} application(s).\n"
            "   Running in LENIENT mode - server will continue.\n\n"
        )
        for app_id, error in self.validation_errors:
            warning_msg += f"   • {app_id}: {error}\n"

        print_yellow(warning_msg)


class TrustedServicesServer(ServerApi):

    def __init__(self, runtime_directory: str) -> None:
        logging.basicConfig(
            filename="log_file.log",
            # level=logging.INFO,  # could be DEBUG, WARNING, ERROR
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filemode="w",
        )
        logger = logging.getLogger("TrustedServicesServer")
        logger.critical("TrustedServicesServer.__init__")

        self.runtime_directory = runtime_directory

        # Initialize validator with mode from environment
        validation_mode = os.getenv("APP_VALIDATION_MODE", "strict")
        self.validator = AppValidator(validation_mode)

        self.apps: dict[str, App] = {}  # To be ovedrriden in reload_apps
        self.reload_apps()

    def reload_apps(self) -> None:
        apps_subdirectory = Path(self.runtime_directory + "/apps")
        app_ids = sorted([p.name for p in apps_subdirectory.iterdir() if p.is_dir()])

        self.apps: dict[str, App] = {
            app_id: App(
                self.runtime_directory,
                app_id,
            )
            for app_id in app_ids
        }

        # Validate loaded applications
        self.validator.validate_apps(self.apps)

        # Post-load validation: scan application Python sources for field ids
        # referenced via request.field_values[...] and warn if any referenced
        # id is not present in the case model. This helps catch typos between
        # decision engine code and the workbook case_fields.
        pattern = re.compile(r"field_values\s*\[\s*['\"]([^'\"]+)['\"]\s*\]")
        for app_id, app in self.apps.items():
            try:
                # Collect all case field ids across locales for this app
                defined_ids: set[str] = set()
                for locale, localized in app.localized_apps.items():
                    try:
                        cf_ids = [f.id for f in localized.case_model.case_fields]
                        defined_ids.update(cf_ids)
                    except Exception as exc:
                        logging.getLogger(__name__).warning(
                            "Skipping case fields for app %s locale %s: %s",
                            app_id,
                            locale,
                            exc,
                        )
                        continue

                # Scan python files under the app directory
                app_dir = Path(self.runtime_directory) / "apps" / app_id
                referenced_ids: set[str] = set()
                for py in app_dir.rglob("*.py"):
                    try:
                        text = py.read_text(encoding="utf-8")
                    except Exception as exc:
                        logging.getLogger(__name__).warning(
                            "Skipping file %s while scanning case fields: %s",
                            py,
                            exc,
                        )
                        continue
                    for m in pattern.finditer(text):
                        referenced_ids.add(m.group(1))

                missing = sorted(referenced_ids - defined_ids)
                if missing:
                    logging.getLogger(__name__).warning(
                        "App '%s': referenced case field ids not found in case_fields: %s",
                        app_id,
                        missing,
                    )
            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Error while validating case fields for app %s: %s",
                    app_id,
                    e,
                )

    def get_app_ids(self) -> list[str]:
        return list(self.apps.keys())

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        app: App = self.apps.get(app_id, None)
        if app is None:
            return []
        return app.get_locales(app_id)

    def get_llm_config_ids(self, app_id: str) -> list[str]:
        app: App = self.apps.get(app_id, None)
        if app is None:
            return []
        return app.get_llm_config_ids(app_id)

    def get_decision_engine_config_ids(self, app_id: str) -> list[str]:
        app: App = self.apps.get(app_id, None)
        if app is None:
            return []
        return app.get_decision_engine_config_ids(app_id)

    def get_app_name(self, app_id: str, locale: SupportedLocale) -> str:
        # TODO Catch exception
        return self.apps[app_id].get_app_name(app_id, locale)

    def get_app_description(self, app_id: str, locale: SupportedLocale) -> str:
        return self.apps[app_id].get_app_description(app_id, locale)

    def get_sample_message(self, app_id: str, locale: SupportedLocale) -> str:
        return self.apps[app_id].get_sample_message(app_id, locale)

    def get_case_model(self, app_id: str, locale: SupportedLocale) -> CaseModel:
        return self.apps[app_id].get_case_model(app_id, locale)

    def analyze(
        self,
        app_id: str,
        locale: SupportedLocale,
        field_values: dict[str, Any],
        text: str,
        read_from_cache: bool,
        llm_config_id: str,
    ) -> dict[str, Any]:
        return self.apps[app_id].analyze(
            app_id,
            locale,
            field_values,
            text,
            read_from_cache,
            llm_config_id,
        )

    def save_text_analysis_cache(
        self,
        app_id: str,
        locale: SupportedLocale,
        text_analysis_cache: str,
    ) -> None:
        self.apps[app_id].save_text_analysis_cache(app_id, locale, text_analysis_cache)

    def handle_case(
        self,
        app_id: str,
        locale: SupportedLocale,
        request: CaseHandlingRequest,
    ) -> CaseHandlingDetailedResponse:
        return self.apps[app_id].handle_case(app_id, locale, request)
