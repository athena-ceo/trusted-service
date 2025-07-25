from src.common.configuration import SupportedLocale
from src.common.localization import Localization


class FrontendLocalization(Localization):
    label_show_details: str
    label_context: str
    label_request: str
    label_please_describe_your_request: str
    label_next_step: str
    label_text_analysis: str
    label_prompt: str
    label_intent_scoring: str
    label_feature_extraction: str
    label_intentions_scored_by_ai: str
    label_data_extracted_by_ai: str
    label_additional_information: str
    label_confirm_your_request: str
    label_submit: str
    label_task: str
    label_logging: str
    label_rule_engine_invocation: str
    label_processing_of_the_request: str
    label_proposed_response: str


# IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
# Add here support for new languages


frontend_localizations: dict[SupportedLocale, FrontendLocalization] = {
    "en": FrontendLocalization(
        label_show_details="Show details",
        label_context="Context",
        label_request="Request",
        label_please_describe_your_request="Please describe your request",
        label_next_step="Next step",
        label_text_analysis="Text analysis",
        label_prompt="Prompt",
        label_intent_scoring="Intent scoring",
        label_feature_extraction="Feature extraction",
        label_intentions_scored_by_ai="Intentions scored by AI",
        label_data_extracted_by_ai="Data extracted by AI",
        label_additional_information="Additional information",
        label_confirm_your_request="Please confirm your request",
        label_submit="Submit",
        label_task="Task",
        label_logging="Logging",
        label_rule_engine_invocation="Rule engine invocation",
        label_processing_of_the_request="Processing of the request",
        label_proposed_response="Proposed response",
    ),
    "fr": FrontendLocalization(
        label_show_details="Montrer les détails",
        label_context="Contexte de la demande",
        label_request="Demande",
        label_please_describe_your_request="Veuillez décrire votre demande",
        label_next_step="Etape suivante",
        label_text_analysis="Analyse du texte",
        label_prompt="Prompt",
        label_intent_scoring="Scoring des intentionss",
        label_feature_extraction="Extraction des features",
        label_intentions_scored_by_ai="Scoring des intentions par l'IA",
        label_data_extracted_by_ai="Extraction d'information par l'IA",
        label_additional_information="Informations complémentaires",
        label_confirm_your_request="Merci de confirmer votre demande",
        label_submit="Soumettre votre demande",
        label_task="Tâche",
        label_logging="Logging",
        label_rule_engine_invocation="Appel au moteur de règles",
        label_processing_of_the_request="Traitement de la demande",
        label_proposed_response="Résponse proposée",
    )
}
