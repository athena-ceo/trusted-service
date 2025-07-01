from typing import Literal, cast, Self, Any, Type

from pydantic import BaseModel, field_validator, Field

from src.common.configuration import Configuration, load_configuration_from_workbook, SupportedLocale

class Option(BaseModel):
    id: str
    label: str


class OptionConfiguration(Configuration):
    options: list[Option]


def load_option_configuration_from_workbook(filename: str, locale: SupportedLocale) -> OptionConfiguration:
    configuration: Configuration = load_configuration_from_workbook(filename=filename,
                                                                    main_tab=None,
                                                                    collections=[("options", Option)],
                                                                    configuration_type=OptionConfiguration,
                                                                    locale=locale)
    option_configuration: OptionConfiguration = cast(OptionConfiguration, configuration)

    return option_configuration

class CaseField(BaseModel):
    id: str
    type: str
    # type: Type[Any]
    label: str
    option_ids_csv: str
    options: list[Option]  = Field(default_factory=list)
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

    # def get_type(self) -> type:
    #     try:
    #         type_: type = eval(self.type)
    #
    #     except NameError:
    #         values = [word.strip() for word in self.type.split(",")]
    #         type_ = Literal[*values]
    #
    #     print(type_)
    #     return type_

    # @field_validator('type', mode='before')
    # @classmethod
    # def convert_type(cls, v):
    #     if isinstance(v, type):
    #         return v
    #     elif isinstance(v, str):
    #         return eval(v)
    #     else:
    #         raise TypeError(f"Invalid type value: {v}")

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


class CaseModelConfiguration(Configuration):
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


def load_case_model_configuration_from_workbook(filename: str, locale: SupportedLocale) -> CaseModelConfiguration:
    configuration: Configuration = load_configuration_from_workbook(filename=filename,
                                                                    main_tab=None,
                                                                    collections=[("case_fields", CaseField)],
                                                                    configuration_type=CaseModelConfiguration,
                                                                    locale=locale)
    case_model_configuration: CaseModelConfiguration = cast(CaseModelConfiguration, configuration)

    return case_model_configuration
