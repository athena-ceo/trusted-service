from __future__ import annotations

import importlib
import json
import time
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, ValidationError

from src.backend.backend.paths import get_app_def_filename, get_cache_file_path
from src.backend.distribution.distribution_email.distribution_email import (
    CaseHandlingDistributionEngineEmail,
)
from src.backend.distribution.distribution_email.distribution_email_config import (
    DistributionEmailConfig,
    load_email_config_from_workbook,
)
from src.backend.text_analysis.text_analyzer import (
    TextAnalysisConfig,
    TextAnalyzer,
    load_text_analysis_config_from_workbook,
)
from src.common.case_model import (
    CaseModel,
    CaseModelConfig,
    load_case_model_config_from_workbook,
)
from src.common.config import Config, SupportedLocale, load_config_from_workbook
from src.common.logging import print_blue, print_red
from src.common.server_api import (
    CaseHandlingDecisionInput,
    CaseHandlingDecisionOutput,
    CaseHandlingDetailedResponse,
    CaseHandlingRequest,
    CaseHandlingResponse,
    ServerApi,
)

if TYPE_CHECKING:
    from src.backend.backend.app import App
    from src.backend.distribution.distribution import CaseHandlingDistributionEngine
    from src.backend.text_analysis.llm import LlmConfig


class Message(BaseModel):
    key: str
    text: str


class LocalizedAppConfig(Config):
    app_name: str
    app_description: str
    sample_message: str
    distribution_engine: str
    messages_to_agent: list[Message]
    messages_to_requester: list[Message]


def load_localized_app_config_from_workbook(
    filename: str,
    locale: SupportedLocale,
) -> LocalizedAppConfig:
    conf: Config = load_config_from_workbook(
        filename=filename,
        main_tab="localized_app",
        collections=[
            ("messages_to_agent", Message),
            ("messages_to_requester", Message),
        ],
        config_type=LocalizedAppConfig,
        locale=locale,
    )

    return cast(LocalizedAppConfig, conf)


class LocalizedApp(ServerApi):

    def __init__(
        self,
        runtime_directory: str,
        app_id: str,
        parent_app: App,
        locale: SupportedLocale,
    ) -> None:

        self.runtime_directory: str = runtime_directory
        self.app_id: str = app_id
        self.parent_app: App = parent_app
        self.locale: SupportedLocale = locale

        # READ FROM localized_app_config

        app_def_filename = get_app_def_filename(runtime_directory, app_id)
        localized_app_config = load_localized_app_config_from_workbook(
            app_def_filename,
            locale,
        )

        self.app_name: str = localized_app_config.app_name
        self.app_description: str = localized_app_config.app_description
        self.sample_message: str = localized_app_config.sample_message

        self.case_handling_distribution_engine: (
            CaseHandlingDistributionEngine | None
        ) = None
        if localized_app_config.distribution_engine == "email":
            email_config: DistributionEmailConfig = load_email_config_from_workbook(
                app_def_filename,
                locale,
            )

            # Clean any problematic characters from config to avoid ASCII encoding errors
            def clean_string(s):
                if isinstance(s, str):
                    # Replace non-breaking space and other problematic characters
                    return s.replace("\xa0", " ").replace("\u00a0", " ")
                return s

            # Clean all string fields in config
            email_config.hub_email_address = clean_string(
                email_config.hub_email_address,
            )
            email_config.agent_email_address = clean_string(
                email_config.agent_email_address,
            )
            if email_config.password:
                email_config.password = clean_string(email_config.password)
            email_config.smtp_server = clean_string(email_config.smtp_server)
            if email_config.smtp_username:
                email_config.smtp_username = clean_string(email_config.smtp_username)

            self.case_handling_distribution_engine = (
                CaseHandlingDistributionEngineEmail(email_config, locale)
            )
        else:  # Ticketing system, etc...
            pass

        self.messages_to_agent: list[Message] = localized_app_config.messages_to_agent
        self.messages_to_requester: list[Message] = (
            localized_app_config.messages_to_requester
        )

        #####

        case_model_config: CaseModelConfig = load_case_model_config_from_workbook(
            app_def_filename,
            locale,
        )
        print_blue(
            f"Loaded {len(case_model_config.case_fields)} case fields for app '{app_id}' locale '{locale}'",
        )

        case_model: CaseModel = CaseModel(case_fields=case_model_config.case_fields)
        self.case_model: CaseModel = case_model
        print_blue(
            f"Initialized case model for app '{app_id}' locale '{locale}' with {len(self.case_model.case_fields)} fields",
        )
        # for field in self.case_model.case_fields:
        #     print_blue(f"  Field: id='{field.id}', label='{field.label}'")
        # print_blue("...")

        self.text_analysis_config: TextAnalysisConfig = (
            load_text_analysis_config_from_workbook(app_def_filename, locale)
        )
        self.text_analyzer = TextAnalyzer(
            runtime_directory,
            app_id,
            locale,
            case_model,
            self.text_analysis_config,
        )

    # API implementation

    def reload_apps(self) -> None:
        pass

    def get_app_ids(self) -> list[str]:
        pass

    def get_locales(self, app_id: str) -> list[SupportedLocale]:
        pass

    def get_llm_config_ids(self, app_id: str) -> list[str]:
        pass

    def get_decision_engine_config_ids(self, app_id: str) -> list[str]:
        pass

    def get_app_name(self, app_id: str, locale: SupportedLocale) -> str:
        return self.app_name

    def get_app_description(self, app_id: str, locale: SupportedLocale) -> str:
        return self.app_description

    def get_sample_message(self, app_id: str, locale: SupportedLocale) -> str:
        return self.sample_message

    def get_case_model(self, app_id: str, locale: SupportedLocale) -> CaseModel:
        return self.case_model

    def _create_fallback_response(
        self,
        locale: SupportedLocale,
        llm_config: LlmConfig,
        exception: Exception,
    ) -> dict[str, Any]:
        """Crée une réponse minimale en cas d'échec de l'analyse LLM.

        Args:
        ----
            locale: La locale pour adapter les messages
            llm_config: La configuration LLM utilisée
            exception: L'exception qui a causé l'échec

        Returns:
        -------
            dict: Structure de réponse minimale avec uniquement l'intention "Autre"/"Other"

        """
        import traceback

        from src.backend.text_analysis.base_models import FIELD_NAME_SCORINGS
        from src.backend.text_analysis.text_analysis_localization import (
            text_analysis_localizations,
        )
        from src.common.constants import (
            KEY_ANALYSIS_RESULT,
            KEY_HASH_CODE,
            KEY_HIGHLIGHTED_TEXT_AND_FEATURES,
            KEY_MARKDOWN_TABLE,
            KEY_PROMPT,
            KEY_STATISTICS,
        )

        # Obtenir les messages localisés
        localization = text_analysis_localizations[locale]
        label_other = localization.label_intention_other

        # Construire le message d'erreur détaillé
        error_type = type(exception).__name__
        error_message = str(exception)
        error_traceback = traceback.format_exc()

        # Code d'erreur court (type + message tronqué)
        error_code = f"{error_type}: {error_message[:200]}"

        # Message d'erreur complet avec traceback
        error_message_full = (
            f"{error_type}: {error_message}\n\nTraceback:\n{error_traceback}"
        )

        # Créer l'intention "Autre" avec score 1 et justification localisée
        intention_other = {
            "intention_id": "other",
            "score": 1,
            "justification": f"{localization.error_justification_prefix}{error_code}",
            "intention_label": label_other,
            "intention_fields": [],
        }

        # Créer les statistiques avec le code d'erreur et le message d'erreur complet
        statistics = {
            "LLM config": llm_config.id,
            "LLM": llm_config.llm,
            "LLM Model": llm_config.model,
            "Prompt format": llm_config.prompt_format,
            "Response time": "0.00s",
            "Error code": error_code,
            "Error Message": error_message_full,
            "Prompt tokens": "N/A",
            "Completion tokens": "N/A",
        }

        # Créer l'analysis_result minimal
        analysis_result = {
            FIELD_NAME_SCORINGS: [intention_other],
            KEY_STATISTICS: statistics,
            KEY_HASH_CODE: None,
        }

        # Générer le markdown table en utilisant la fonction existante
        from src.backend.rendering.md import build_markdown_table_intentions

        markdown_table = build_markdown_table_intentions(analysis_result)

        # Créer la réponse complète avec la structure attendue
        return {
            KEY_ANALYSIS_RESULT: analysis_result,
            KEY_PROMPT: "",
            KEY_MARKDOWN_TABLE: markdown_table,
            KEY_HIGHLIGHTED_TEXT_AND_FEATURES: "",
        }

    def analyze(
        self,
        app_id: str,
        locale: SupportedLocale,
        field_values: dict[str, Any],
        text: str,
        read_from_cache: bool,
        llm_config_id: str,
    ) -> dict[str, Any]:
        """Analyse le texte avec mécanisme de retry pour les erreurs temporaires.

        En cas d'erreur lors de l'analyse, réessaie jusqu'à 3 fois avec un délai de 2 secondes
        entre chaque tentative. Si toutes les tentatives échouent, retourne une réponse minimale
        avec uniquement l'intention "Autre"/"Other" et le code d'erreur dans les statistiques.
        """
        llm_configs: dict[str, LlmConfig] = self.parent_app.llm_configs
        llm_config: LlmConfig = llm_configs[llm_config_id]

        # Nombre maximum de tentatives
        max_retries = 3
        # Délai entre les tentatives en secondes
        retry_delay = 2.0

        for attempt in range(1, max_retries + 1):
            try:
                return self.text_analyzer.analyze(
                    locale=locale,
                    llm_config=llm_config,
                    field_values=field_values,
                    text=text,
                    read_from_cache=read_from_cache,
                )
            except Exception as e:
                if attempt < max_retries:
                    # Erreur temporaire : on réessaie après un délai
                    print_red(
                        f"⚠️  Erreur lors de l'analyse (tentative {attempt}/{max_retries}): {type(e).__name__}: {str(e)[:200]}",
                    )
                    print_blue(f"   Nouvelle tentative dans {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                else:
                    # Dernière tentative échouée : on retourne une réponse minimale au lieu de propager l'exception
                    error_code = f"{type(e).__name__}: {str(e)[:200]}"
                    print_red(
                        f"❌ Échec de l'analyse après {max_retries} tentatives: {error_code}",
                    )
                    print_blue(
                        "   Retour d'une réponse minimale avec l'intention 'Autre'",
                    )
                    return self._create_fallback_response(locale, llm_config, e)
        return None

    def save_text_analysis_cache(
        self,
        app_id: str,
        locale: SupportedLocale,
        text_analysis_cache: str,
    ) -> None:
        print_blue("SAVING")
        print_blue(text_analysis_cache)
        text_analysis_cache_dict = json.loads(text_analysis_cache)
        print_blue()
        hash_code = text_analysis_cache_dict["hash_code"]
        cache_filename = get_cache_file_path(
            self.runtime_directory,
            self.app_id,
            self.locale,
            hash_code,
        )
        with open(file=cache_filename, mode="w", encoding="utf-8") as f:
            f.write(text_analysis_cache)

    @staticmethod
    def verbalize(list_verbalized_messages: list[Message], message_to_verbalize: str):
        # if s starts with a "#" and is the key of a registered message to requester, then replace it with its text
        if message_to_verbalize.startswith("#"):
            words = [word.strip() for word in message_to_verbalize[1:].split(",")]
            if words:
                key = words[0]
                if key:
                    # Look for key in config
                    if m := [m for m in list_verbalized_messages if m.key == key]:
                        format_string = m[
                            0
                        ].text  # A string that potentially contains {0}, {1}, {2}, etc
                        values = words[1:]
                        return format_string.format(*values)
        return message_to_verbalize

    def handle_case(
        self,
        app_id: str,
        locale: SupportedLocale,
        request: CaseHandlingRequest,
    ) -> CaseHandlingDetailedResponse:

        # Data enrichment
        if self.parent_app.data_enrichment:
            module_name, function_name = self.parent_app.data_enrichment.rsplit(".", 1)
            module = importlib.import_module(module_name)
            func = getattr(module, function_name)
            func(request.field_values)

        # Validate presence of required fields before building decision input
        missing_fields = [
            case_field.id
            for case_field in self.case_model.case_fields
            if case_field.send_to_decision_engine
            and case_field.id not in request.field_values
        ]
        if missing_fields:
            msg = f"Missing required field_values for decision engine: {', '.join(missing_fields)}"
            raise ValueError(
                msg,
            )

        # Filter-out the field values that are not to be sent to the decision engine
        field_values: dict[str, Any] = {}
        for case_field in self.case_model.case_fields:
            if case_field.send_to_decision_engine:
                field_values[case_field.id] = request.field_values.get(case_field.id)

        case_handling_decision_input = CaseHandlingDecisionInput(
            intention_id=request.intention_id,
            field_values=field_values,
        )

        case_handling_decision_output: CaseHandlingDecisionOutput = (
            self.parent_app.decide(
                request.decision_engine_config_id,
                case_handling_decision_input,
            )
        )

        try:
            CaseHandlingDecisionOutput.model_validate(case_handling_decision_output)
        except ValidationError as exc:
            print_red("ValidationError", repr(exc.errors()[0]["type"]))
            print_red(exc.json(indent=4))
            print_blue(case_handling_decision_output)
            print_blue(case_handling_decision_output.handling)
            print_blue(case_handling_decision_output.acknowledgement_to_requester)
            print_blue(case_handling_decision_output.response_template_id)
            print_blue(case_handling_decision_output.work_basket)
            print_blue(case_handling_decision_output.priority)
            print_blue(case_handling_decision_output.notes)
            print_blue(case_handling_decision_output.details)

        # A verbalized copy of case_handling_decision_output
        verbalized_case_handling_decision_output = case_handling_decision_output.copy(
            deep=True,
        )
        notes = verbalized_case_handling_decision_output.notes
        verbalized_case_handling_decision_output.notes = [
            self.verbalize(self.messages_to_agent, note) for note in notes
        ]
        verbalized_case_handling_decision_output.acknowledgement_to_requester = (
            self.verbalize(
                self.messages_to_requester,
                verbalized_case_handling_decision_output.acknowledgement_to_requester,
            )
        )

        intent_label = None

        # Si l'intention est "other", utiliser le label de localisation car cette intention
        # n'est pas dans text_analysis_config.intentions (elle est créée dynamiquement)
        if request.intention_id == "other":
            intent_label = self.text_analyzer.localization.label_intention_other
        else:
            for intent in self.text_analysis_config.intentions:
                if intent.id == request.intention_id:
                    intent_label = intent.label

        if self.case_handling_distribution_engine is None:
            msg = (
                "No distribution engine configured for this app/locale. "
                "Configure distribution_engine in the workbook (e.g., 'email') or provide a custom implementation."
            )
            raise ValueError(
                msg,
            )

        rendering_email_to_agent, rendering_email_to_requester = (
            self.case_handling_distribution_engine.distribute(
                self.case_model,  # TODO avoid passing this
                request,
                intent_label,
                verbalized_case_handling_decision_output,
            )
        )

        case_handling_response: CaseHandlingResponse = CaseHandlingResponse(
            acknowledgement_to_requester=verbalized_case_handling_decision_output.acknowledgement_to_requester,
            case_handling_report=(
                rendering_email_to_agent,
                rendering_email_to_requester,
            ),
        )

        print_red(type(case_handling_decision_output), case_handling_decision_output)

        return CaseHandlingDetailedResponse(
            case_handling_decision_input=case_handling_decision_input,
            case_handling_decision_output=case_handling_decision_output,
            case_handling_response=case_handling_response,
        )
