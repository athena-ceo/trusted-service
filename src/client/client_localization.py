from __future__ import annotations

from typing import TYPE_CHECKING

from src.common.localization import Localization

if TYPE_CHECKING:
    from src.common.config import SupportedLocale


class ClientLocalization(Localization):
    label_show_details: str
    label_context: str
    label_yes: str
    label_no: str
    label_request: str
    label_please_describe_your_request: str
    label_next_step: str
    label_text_analysis: str
    label_save_to_cache: str
    label_prompt: str
    label_intent_scoring: str
    label_feature_extraction: str
    label_misc: str
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


frontend_localizations: dict[SupportedLocale, ClientLocalization] = {
    "en": ClientLocalization(
        label_show_details="Show details",
        label_context="Context",
        label_yes="Yes",
        label_no="No",
        label_request="Request",
        label_please_describe_your_request="Please describe your request",
        label_next_step="Next step",
        label_text_analysis="Text analysis",
        label_save_to_cache="Save text analysis to cache",
        label_prompt="Prompt",
        label_intent_scoring="Intent scoring",
        label_feature_extraction="Feature extraction",
        label_misc="Misc",
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
    "fr": ClientLocalization(
        label_show_details="Montrer les détails",
        label_context="Contexte de la demande",
        label_yes="Oui",
        label_no="Non",
        label_request="Demande",
        label_please_describe_your_request="Veuillez décrire votre demande",
        label_next_step="Etape suivante",
        label_text_analysis="Analyse du texte",
        label_save_to_cache="Sauver l'analyse du texte en cache",
        label_prompt="Prompt",
        label_intent_scoring="Scoring des intentions",
        label_feature_extraction="Extraction des features",
        label_misc="Divers",
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
    ),
    "fi": ClientLocalization(
        label_show_details="Näytä yksityiskohdat",
        label_context="Asiayhteys",
        label_yes="kyllä",
        label_no="ei",
        label_request="Pyyntö",
        label_please_describe_your_request=" Miten voin auttaa?",
        label_next_step="Seuraava askel",
        label_text_analysis="Tekstianalyysi",
        label_save_to_cache="Tallenna tekstianalyysi välimuistiin",
        label_prompt="Kehote",
        label_intent_scoring="Aikomuksen pisteytys",
        label_feature_extraction="Ominaisuuksien poiminta",
        label_misc="Sekalaista",
        label_intentions_scored_by_ai="AI:n pisteyttämät aikomukset",
        label_data_extracted_by_ai="AI:n poimima data",
        label_additional_information="Lisätieto",
        label_confirm_your_request="Vahvista pyyntösi",
        label_submit="Suorita",
        label_task="Tehtävä",
        label_logging="Kirjaus",
        label_rule_engine_invocation="Sääntökoneen hyödyntäminen",
        label_processing_of_the_request="Pyynnön prosessointi",
        label_proposed_response="Ehdotettu vastaus",
    ),
}
