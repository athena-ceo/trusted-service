from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal, cast

from openpyxl.reader.excel import load_workbook
from pydantic import BaseModel, Field, field_validator

from src.common.config import (
    Config,
    SupportedLocale,
    load_dicts_from_worksheet,
    load_pydantic_objects_from_worksheet,
)

if TYPE_CHECKING:
    from openpyxl.workbook import Workbook


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
    help: str = ""
    format: str = (
        ""  # format should be one of YYYY/MM/DD, DD/MM/YYYY, or MM/DD/YYYY and can also use a period (.) or hyphen (-) as separators
    )
    allowed_values_list_name: str = ""
    allowed_values: list[OptionalListElement] = Field(default_factory=list)
    default_value: Any = None

    # Fields required in UI
    scope: Literal["CONTEXT", "REQUESTER"]
    show_in_ui: bool
    intention_ids: list[str]

    # Fields required for Text Analysis
    description: str
    extraction: Literal["DO NOT EXTRACT", "EXTRACT", "EXTRACT AND HIGHLIGHT"]

    # Fields required for integration of decision engine
    send_to_decision_engine: bool

    @field_validator("intention_ids", mode="before")
    @classmethod
    def convert_intention_ids(cls, v):
        if isinstance(v, list):
            return v
        elif v is None:
            return []
        elif isinstance(v, str):
            return v.split()
        else:
            msg = f"Invalid type value: {v}"
            raise TypeError(msg)


class CaseModelConfig(Config):
    case_fields: list[CaseField]


class CaseModel(BaseModel):
    case_fields: list[CaseField]

    def get_field_by_id(self, field_id: str) -> CaseField:
        for field in self.case_fields:
            if field.id == field_id:
                return field
        msg = f"Field with id '{field_id}' not found in case model."
        raise ValueError(msg)


class Case(BaseModel):
    field_values: dict[str, Any]  # Field id, field value

    @staticmethod
    def create_default_instance(case_model: CaseModel):
        field_values: dict[str, Any] = {
            field.id: field.default_value for field in case_model.case_fields
        }
        return Case(field_values=field_values)


def load_case_model_config_from_workbook(
    filename: str,
    locale: SupportedLocale,
) -> CaseModelConfig:
    logger = logging.getLogger(__name__)

    # Load raw dicts with Excel row numbers so we can warn about missing important fields
    config_workbook: Workbook = load_workbook(filename)
    worksheet = config_workbook["case_fields"]
    dicts_with_rows = load_dicts_from_worksheet(worksheet, locale, include_row=True)

    # Important fields to check for emptiness
    important_fields = ["help", "format", "allowed_values_list_name"]
    missing_map: dict[str, list[int]] = {f: [] for f in important_fields}

    for rownum, data in dicts_with_rows:
        # defensive checks: ensure we have a mapping
        if not isinstance(data, dict):
            continue
        for f in important_fields:
            val = data.get(f)
            if val is None or isinstance(val, str) and val.strip() == "":
                missing_map[f].append(int(rownum))

    # Emit warnings if any important field is missing in any rows
    for f, rows in missing_map.items():
        if rows:
            logger.warning(
                "case_fields: column '%s' is empty for rows: %s in workbook %s",
                f,
                rows,
                filename,
            )

    # Normalize None values for important string fields so Pydantic will accept them
    normalized: list[dict] = []
    for _row, data in dicts_with_rows:
        if not isinstance(data, dict):
            continue
        for f in important_fields:
            if data.get(f) is None:
                data[f] = ""
        normalized.append(data)

    # Validate models
    case_field_models: list[CaseField] = [
        CaseField.model_validate(data) for data in normalized
    ]
    case_model_config = CaseModelConfig(case_fields=case_field_models)

    # If the field has an associated list of allowed values, get the values from the matching tab
    for case_field in case_model_config.case_fields:
        if case_field.allowed_values_list_name:
            worksheet = config_workbook[case_field.allowed_values_list_name]
            allowed_values: list[BaseModel] = load_pydantic_objects_from_worksheet(
                worksheet,
                OptionalListElement,
                locale,
            )
            case_field.allowed_values = [
                cast(OptionalListElement, e) for e in allowed_values
            ]

    return case_model_config
