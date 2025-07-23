from pydantic import BaseModel, Field, field_validator

FIELD_NAME_SCORINGS = "scorings"
PREFIX_FRAGMENTS = "fragments_"


class Definition(BaseModel):
    """A definition to give context to the LLM."""
    term: str = Field(..., description="Term to score")
    definition: str = Field(..., description="Natural-language definition")


class Intention(BaseModel):
    """One intention you want to score in the text."""
    id: str = Field(..., description="Unique ID of the intention")
    label: str = Field(..., description="Label of the intention")
    description: str = Field(..., description="Natural-language description")


class Feature(BaseModel):
    id: str
    label: str
    type: type
    description: str
    highlight_fragments: bool

    # REMOVE
    @field_validator('type', mode='before')
    @classmethod
    def convert_type(cls, v):
        # print("cls", cls)
        if isinstance(v, type):
            return v
        if v == "int":
            return int
        if v == "float":
            return float
        if v == "bool":
            return bool
        if v == "str" or v == "date":
            return str
        raise TypeError(f"Invalid type value: {v}")


# class Test(BaseModel):
#     text: str
#     expected_intention: str
