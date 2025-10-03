from src.common.localization import Localization

from src.common.config import SupportedLocale


class DistributionEngineEmaiLocalization(Localization):
    label_intent: str
    label_yes: str
    label_no: str
    label_notes: str


# IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
# Add here support for new languages
distribution_engine_email_localizations: dict[SupportedLocale, DistributionEngineEmaiLocalization] = {

    "en": DistributionEngineEmaiLocalization(
        label_intent="Intent",
        label_yes="yes",
        label_no="no",
        label_notes="Important notes"),

    "fr": DistributionEngineEmaiLocalization(
        label_intent="Intention",
        label_yes="oui",
        label_no="non",
        label_notes="Eléments importants"),

    "fi": DistributionEngineEmaiLocalization(
        label_intent="aikomus",
        label_yes="kyllä",
        label_no="ei",
        label_notes="tärkeät muistiinpanot"),

}
