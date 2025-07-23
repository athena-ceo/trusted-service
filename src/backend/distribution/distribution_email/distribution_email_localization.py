from src.common.localization import Localization

from src.common.configuration import SupportedLocale


class DistributionEngineEmailocalization(Localization):
    label_yes: str
    label_no: str
    label_alerts: str


# IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
# Add here support for new languages
distribution_engine_email_localizations: dict[SupportedLocale, DistributionEngineEmailocalization] = {
    "en": DistributionEngineEmailocalization(
        label_yes="yes",
        label_no="no",
        label_alerts="Alerts"),
    "fr": DistributionEngineEmailocalization(
        label_yes="oui",
        label_no="non",
        label_alerts="Alertes")
}
