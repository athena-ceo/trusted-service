from src.common.localization import Localization

from src.common.config import SupportedLocale


class DistributionEngineEmaiLocalization(Localization):
    label_intent: str
    label_yes: str
    label_no: str
    label_notes: str
    label_reply: str
    label_response_to_requester: str
    label_response_default_subject: str
    label_very_high: str
    label_high: str
    label_medium: str
    label_low: str
    label_very_low: str


# IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
# Add here support for new languages
distribution_engine_email_localizations: dict[SupportedLocale, DistributionEngineEmaiLocalization] = {

    "en": DistributionEngineEmaiLocalization(
        label_intent="Intent",
        label_yes="yes",
        label_no="no",
        label_notes="Important notes",
        label_reply="Reply to the sender",
        label_response_to_requester="Response displayed to the requester",
        label_response_default_subject="Your request to the French government services",
        label_very_high="VERY_HIGH",
        label_high="HIGH",
        label_medium="MEDIUM",
        label_low="LOW",
        label_very_low="VERY_LOW"),

    "fr": DistributionEngineEmaiLocalization(
        label_intent="Intention",
        label_yes="oui",
        label_no="non",
        label_notes="Eléments importants",
        label_reply="Répondre à l'expéditeur ",
        label_response_to_requester="Réponse affichée au demandeur",
        label_response_default_subject="Votre demande auprès des services de l'État",
        label_very_high="TRES_HAUTE",
        label_high="HAUTE",
        label_medium="NORMALE",
        label_low="BASSE",
        label_very_low="TRES_BASSE"),

    "fi": DistributionEngineEmaiLocalization(
        label_intent="aikomus",
        label_yes="kyllä",
        label_no="ei",
        label_notes="tärkeät muistiinpanot",
        label_reply="Vastaa lähettäjälle",
        label_response_to_requester="Vastaus näytetään pyytäjälle",
        label_response_default_subject="Pyyntösi Ranskan hallintoviranomaisille",
        label_very_high="ERITTAIN_KORKEA",
        label_high="KORKEA",
        label_medium="NORMAALI",
        label_low="MATALA",
        label_very_low="ERITTAIN_MATALA"),
}
