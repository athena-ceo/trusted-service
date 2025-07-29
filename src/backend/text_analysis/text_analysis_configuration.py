from typing import Literal, cast

from src.backend.text_analysis.base_models import Intention, Definition
from src.common.configuration import Configuration, load_configuration_from_workbook, SupportedLocale


class TextAnalysisConfiguration(Configuration):
    # locale: Literal["en", "fr"]

    # LLM
    llm: Literal["openai", "ollama", "scaleway"]
    model: str
    response_format_type: Literal["json_object", "pydantic_model"]
    # Ollama and Scaleway do not support Pydantic models, so this is only for OpenAI
    prompt_format: Literal["markdown", "text"]
    temperature: float
    system_prompt_prefix: str

    # Misc
    definitions: list[Definition]
    intentions: list[Intention]
    # tests: list[Test]
    read_from_cache: bool
    save_to_cache: bool


def load_text_analysis_configuration_from_workbook(filename: str, locale: SupportedLocale) -> TextAnalysisConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="text_analysis",
                                                           collections=[("definitions", Definition),
                                                                        ("intentions", Intention),
                                                                        # ("features", Feature),
                                                                        # ("tests", Test)
                                                                        ],
                                                           configuration_type=TextAnalysisConfiguration,
                                                           locale=locale)
    return cast(TextAnalysisConfiguration, conf)

# def get_localization(config: TextAnalysisConfiguration) -> TextAnalysisLocalization:
#     return TextAnalysisLocalizationEn() if config.locale == "en" else TextAnalysisLocalizationFr()
