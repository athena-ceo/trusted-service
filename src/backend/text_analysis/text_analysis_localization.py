from abc import abstractmethod

from src.common.configuration import SupportedLocale
from src.common.localization import Localization


class TextAnalysisLocalization(Localization):
    docstring_scoring_for_one_intention: str
    docstring_scoring_for_one_intention_intention_id: str
    docstring_scoring_for_one_intention_score: str
    docstring_scoring_for_one_intention_justification: str
    docstring_scoring_for_multiple_intentions: str

    promptstring_perform_the_2_tasks_below: str
    promptstring_task: str
    promptstring_instructions_intentions: str
    promptstring_list_of_intentions: str
    promptstring_instructions_extract_features: str
    promptstring_definitions: str
    promptstring_return_only_json: str

    @abstractmethod
    def description_of_fragments_feature(self, description_of_feature: str) -> str:
        pass


class TextAnalysisLocalizationEn(TextAnalysisLocalization):
    def __init__(self):
        super().__init__(
            docstring_scoring_for_one_intention="Model output for a single intention.",
            docstring_scoring_for_one_intention_intention_id="Matches Intention.id",
            docstring_scoring_for_one_intention_score="0 = absent, 10 = fully present",
            docstring_scoring_for_one_intention_justification="Why the model chose this score",
            docstring_scoring_for_multiple_intentions="List scorings for individual intentions",

            promptstring_perform_the_2_tasks_below="Please perform the 2 tasks below",
            promptstring_task="TASK",
            promptstring_instructions_intentions="Given the *user's* text and the list of intentions below, rate each intention between 0 and 10 and justify the rating in one or two sentences.",
            promptstring_list_of_intentions="List of intentions",
            promptstring_instructions_extract_features="Extract the following features from the text",
            promptstring_definitions="DEFINITIONS",
            promptstring_return_only_json="Return ONLY valid JSON that matches this JSON Schema (no extra keys, no prose)",
        )

    def description_of_fragments_feature(self, description_of_feature: str) -> str:
        return f"if the text mentions {description_of_feature}, the list of string fragments that mention it"
        pass


class TextAnalysisLocalizationFr(TextAnalysisLocalization):
    def __init__(self):
        super().__init__(
            docstring_scoring_for_one_intention="Résultat pour une intention unique.",
            docstring_scoring_for_one_intention_intention_id="Correspond à Intention.id",
            docstring_scoring_for_one_intention_score="0 = absence, 10 = forte présence",
            docstring_scoring_for_one_intention_justification="La raison pour laquelle le modèle a déterminé ce score",
            docstring_scoring_for_multiple_intentions="Liste des scorings pour chacune des intentions",

            promptstring_perform_the_2_tasks_below="Merci d'exécuter les 2 tâches suivantes",
            promptstring_task="TACHE",
            promptstring_instructions_intentions="Pour un texte donné fourni par *l'utilisateur* et la liste d'intentions ci-dessous, calculer un score entre 0 et 10 pour chaque intention et justifier le score en une ou deux phrases.",
            promptstring_list_of_intentions="Liste des intentions",
            promptstring_instructions_extract_features="Extraire les éléments suivants du texte",
            promptstring_definitions="DEFINITIONS",
            promptstring_return_only_json="Retourner obligatoirement une structure JSON valide qui matche le schéma JSON suivant (n'ajouter aucun texte parasite)",
        )

    def description_of_fragments_feature(self, description_of_feature: str) -> str:
        return f"si le texte mentionne {description_of_feature}, la liste des fragments de ce texte qui le mentionne"


def get_text_analysis_localization(locale: SupportedLocale) -> TextAnalysisLocalization:
    return TextAnalysisLocalizationEn() if locale == "en" else TextAnalysisLocalizationFr()
