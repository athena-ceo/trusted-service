from typing import Literal, cast, Self, Any

from pydantic import BaseModel, field_validator

from common.src.configuration import Configuration, load_configuration_from_workbook


class CaseField(BaseModel):
    id: str
    type_str: str
    label: str
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

    def get_type(self) -> type:
        return eval(self.type_str)

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


class CaseModel(Configuration):
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


def load_case_model_from_workbook(filename: str) -> CaseModel:
    configuration: Configuration = load_configuration_from_workbook(filename=filename,
                                                                    main_tab=None,
                                                                    collections=[("case_fields", CaseField)],
                                                                    configuration_type=CaseModel)
    case_model: CaseModel = cast(CaseModel, configuration)

    case = Case.create_default_instance(case_model)

    return case_model
