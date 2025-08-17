from typing import Any


def preprocessing(field_values: dict[str, Any]):
    if field_values["surname"] == "Doe":
        field_values["customer_lifetime_value"] = "High"
    else:
        field_values["customer_lifetime_value"] = "Medium"
