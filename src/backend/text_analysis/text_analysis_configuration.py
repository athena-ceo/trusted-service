from typing import Literal, cast

from src.backend.text_analysis.base_models import Intention, Test, Definition
from src.common.configuration import Configuration, load_configuration_from_workbook, SupportedLocale
from src.backend.text_analysis.text_analysis_localization import TextAnalysisLocalization, TextAnalysisLocalizationEn, TextAnalysisLocalizationFr


class TextAnalysisConfiguration(Configuration):
    # locale: Literal["en", "fr"]

    # LLM
    llm: Literal["openai"]
    model: str
    response_format_type: Literal["json_object", "pydantic_model"]
    temperature: float
    system_prompt_prefix: str

    # Misc
    definitions: list[Definition]
    intentions: list[Intention]
    tests: list[Test]
    read_from_cache: bool
    save_to_cache: bool


def load_text_analysis_configuration_from_workbook(filename: str, locale: SupportedLocale) -> TextAnalysisConfiguration:
    conf: Configuration = load_configuration_from_workbook(filename=filename,
                                                           main_tab="text_analysis",
                                                           collections=[("definitions", Definition),
                                                                        ("intentions", Intention),
                                                                        # ("features", Feature),
                                                                        ("tests", Test)],
                                                           configuration_type=TextAnalysisConfiguration,
                                                           locale=locale)
    return cast(TextAnalysisConfiguration, conf)


# def get_localization(config: TextAnalysisConfiguration) -> TextAnalysisLocalization:
#     return TextAnalysisLocalizationEn() if config.locale == "en" else TextAnalysisLocalizationFr()
