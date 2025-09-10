from typing import Any


def data_enrichment(field_values: dict[str, Any]):
    # Simulating the access to a CRM to get the customer's CLTV given his/her name
    if field_values["surname"] == "Doe":
        field_values["customer_lifetime_value"] = "High"
    else:
        field_values["customer_lifetime_value"] = "Medium"
