from src.common.config import SupportedLocale
from src.common.localization import Localization


class TextAnalysisLocalization(Localization):
    docstring_scoring_for_one_intention: str
    docstring_scoring_for_one_intention_intention_id: str
    docstring_scoring_for_one_intention_score: str
    docstring_scoring_for_one_intention_justification: str
    docstring_scoring_for_multiple_intentions: str

    promptstring_prompt_is_markdown: str
    promptstring_intent_id: str
    promptstring_intent_description: str
    promptstring_perform_the_2_tasks_below: str
    promptstring_task: str
    promptstring_instructions_intentions: str
    promptstring_list_of_intentions: str
    promptstring_instructions_extract_features: str
    promptstring_description_of_fragments_feature: str
    promptstring_definitions: str
    promptstring_term: str
    promptstring_definition: str
    promptstring_return_only_json: str

    label_intention_other: str


# IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
# Add here support for new languages

text_analysis_localizations: dict[SupportedLocale, TextAnalysisLocalization] = {
    "en": TextAnalysisLocalization(
        docstring_scoring_for_one_intention="Model output for a single intention.",
        docstring_scoring_for_one_intention_intention_id="Matches Intention.id",
        docstring_scoring_for_one_intention_score="0 = absent, 10 = fully present",
        docstring_scoring_for_one_intention_justification="Why the model chose this score",
        docstring_scoring_for_multiple_intentions="List of the scorings for individual intentions",

        promptstring_prompt_is_markdown="This prompt is written in Markdown format.",
        promptstring_intent_id="Intent id",
        promptstring_intent_description="Intent description",
        promptstring_perform_the_2_tasks_below="Please perform the 2 tasks below",
        promptstring_task="TASK",
        promptstring_instructions_intentions="Given the *user's* text and the list of intentions below, rate each intention between 0 and 10 and justify the rating in one or two sentences.",
        promptstring_list_of_intentions="List of intentions",
        promptstring_instructions_extract_features="Extract the following features from the text",
        promptstring_description_of_fragments_feature="If the text mentions {description_of_feature}, the list of string fragments that mention it",
        promptstring_definitions="Definitions",
        promptstring_term="Term",
        promptstring_definition="Definition",
        promptstring_return_only_json="Return ONLY valid JSON that matches this JSON Schema (no extra keys, no prose)",

        label_intention_other="OTHER", ),

    "fr": TextAnalysisLocalization(
        docstring_scoring_for_one_intention="Résultat pour une intention unique.",
        docstring_scoring_for_one_intention_intention_id="Correspond à Intention.id",
        docstring_scoring_for_one_intention_score="0 = absence, 10 = forte présence",
        docstring_scoring_for_one_intention_justification="La raison pour laquelle le modèle a déterminé ce score",
        docstring_scoring_for_multiple_intentions="Liste des scorings pour chacune des intentions",

        promptstring_prompt_is_markdown="Ce prompt est au format Markdown.",
        promptstring_intent_id="Identifiant de l'intention",
        promptstring_intent_description="Description de l'intention",
        promptstring_perform_the_2_tasks_below="Merci d'exécuter les 2 tâches suivantes",
        promptstring_task="TACHE",
        promptstring_instructions_intentions="Pour un texte donné fourni par *l'utilisateur* et la liste d'intentions ci-dessous, calculer un score entre 0 et 10 pour chaque intention et justifier le score en une ou deux phrases.",
        promptstring_list_of_intentions="Liste des intentions",
        promptstring_instructions_extract_features="Extraire les éléments suivants du texte",
        promptstring_description_of_fragments_feature="si le texte mentionne {description_of_feature}, la liste des fragments de ce texte qui le mentionne",
        promptstring_definitions="Définitions",
        promptstring_term="Terme",
        promptstring_definition="Définition",
        promptstring_return_only_json="Retourner obligatoirement une structure JSON valide qui matche le schéma JSON suivant (n'ajouter aucun texte parasite)",

        label_intention_other="AUTRE"),

    "fi": TextAnalysisLocalization(
        docstring_scoring_for_one_intention="Mallin tuloste yhdestä aikomuksesta.",
        docstring_scoring_for_one_intention_intention_id="vastaa Intention.id",
        docstring_scoring_for_one_intention_score="0 = puuttuu, 10 = täysosuma",
        docstring_scoring_for_one_intention_justification="Miksi malli valitsi tämän pisteytyksen",
        docstring_scoring_for_multiple_intentions="Lista yksittäisen aikomuksen pisteytyksistä",
        promptstring_prompt_is_markdown="Tämä prompti on kirjoitettu Markdown- formaatissa.",
        promptstring_intent_id="Intent id",
        promptstring_intent_description="Aikomuksen kuvaus",
        promptstring_perform_the_2_tasks_below="Tee alla olevat kaksi tehtävää",
        promptstring_task="TEHTÄVÄ",
        promptstring_instructions_intentions="Perustuen *käyttäjän* antamaan tekstiin ja alla olevaan listaan aikomuksista luokittele jokainen aikomus nollasta kymmeneen ja perustele luokittelu yhdellä tai kahdella lauseella.",
        promptstring_list_of_intentions="Lista aikomuksista",
        promptstring_instructions_extract_features="Poimi seuraavat ominaisuudet tekstistä",
        promptstring_description_of_fragments_feature="Jos tekstissä mainitaan {description_of_feature}, lista merkkijonon osista, joissa se mainitaan",
        promptstring_definitions="Määritelmät",
        promptstring_term="Termi",
        promptstring_definition="Määritelmä",
        promptstring_return_only_json="Palauta VAIN validi JSON, joka vastaa kyseistä JSON-mallia (ei ylimääräisiä avaimia, ei proosaa)",
        label_intention_other="MUU", ),

}
