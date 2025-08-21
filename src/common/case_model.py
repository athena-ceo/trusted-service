from typing import Literal, cast, Any

from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from pydantic import BaseModel, field_validator, Field

from src.common.config import Config, load_config_from_workbook, SupportedLocale, load_pydantic_objects_from_worksheet


class OptionalListElement(BaseModel):
    id: str
    label: str
    condition_python: str
    condition_javascript: str

class CaseField(BaseModel):
    id: str
    type: str
    label: str
    mandatory: bool
    help: str
    format: str  # format should be one of YYYY/MM/DD, DD/MM/YYYY, or MM/DD/YYYY and can also use a period (.) or hyphen (-) as separators
    allowed_values_list_name: str
    allowed_values: list[OptionalListElement]  = Field(default_factory=list)
    default_value: Any

    # Fields required in UI
    scope: Literal["CONTEXT", "USER"]
    show_in_ui: bool
    intention_ids: list[str]

    # Fields required for Text Analysis
    description: str
    extraction: Literal["DO NOT EXTRACT", "EXTRACT", "EXTRACT AND HIGHLIGHT"]

    # Fields required for integration of decision engine
    send_to_decision_engine: bool

    @field_validator('intention_ids', mode='before')
    @classmethod
    def convert_intention_ids(cls, v):
        if isinstance(v, list):
            return v
        elif v is None:
            return []
        elif isinstance(v, str):
            return v.split()
        else:
            raise TypeError(f"Invalid type value: {v}")


class CaseModelConfig(Config):
    case_fields: list[CaseField]


class CaseModel(BaseModel):
    case_fields: list[CaseField]

    def get_field_by_id(self, field_id: str) -> CaseField:
        for field in self.case_fields:
            if field.id == field_id:
                return field
        raise ValueError(f"Field with id '{field_id}' not found in case model.")


class Case(BaseModel):
    field_values: dict[str, Any]  # Field id, field value

    @staticmethod
    def create_default_instance(case_model: CaseModel):
        field_values: dict[str, Any] = {
            field.id: field.default_value
            for field in case_model.case_fields
        }
        return Case(field_values=field_values)


def load_case_model_config_from_workbook(filename: str, locale: SupportedLocale) -> CaseModelConfig:
    config: Config = load_config_from_workbook(filename=filename,
                                                      main_tab=None,
                                                      collections=[("case_fields", CaseField)],
                                                      config_type=CaseModelConfig,
                                                      locale=locale)
    case_model_config: CaseModelConfig = cast(CaseModelConfig, config)

    for case_field in case_model_config.case_fields:

        # If the field has an associated list of allowed values, get the values from the matching tab

        if case_field.allowed_values_list_name:
            config_workbook: Workbook = load_workbook(filename)
            worksheet = config_workbook[case_field.allowed_values_list_name]
            allowed_values: list[BaseModel] = load_pydantic_objects_from_worksheet(worksheet, OptionalListElement, locale)
            case_field.allowed_values = [cast(OptionalListElement, e) for e in allowed_values]  # This is cleaner than casting the list

    return case_model_config
