from __future__ import annotations

from typing import TYPE_CHECKING

from src.common.localization import Localization

if TYPE_CHECKING:
    from src.common.config import SupportedLocale


class HTMLLocalization(Localization):
    label_yes: str
    label_no: str


# Add here support for new languages
html_localizations: dict[SupportedLocale, HTMLLocalization] = {
    "en": HTMLLocalization(label_yes="yes", label_no="no"),
    "fr": HTMLLocalization(label_yes="oui", label_no="non"),
    "fi": HTMLLocalization(label_yes="kyllä", label_no="ei"),
}
