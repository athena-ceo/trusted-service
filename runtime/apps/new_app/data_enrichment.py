from typing import Dict, Any

# Trusted Services: data enrichment function
# Adjusts/derives field values based on what the requester provided or defaults.
# Conventions: booleans are encoded as strings: 'True / 'False

EMPTY = "'"
TRUE = "'True"
FALSE = "'False"

def _norm_bool_str(val: Any) -> str:
    if isinstance(val, str):
        low = val.strip().lower()
        if low in {"'true", "true", "yes", "y", "1"}:
            return TRUE
        if low in {"'false", "false", "no", "n", "0"}:
            return FALSE
    if isinstance(val, bool):
        return TRUE if val else FALSE
    return FALSE

def _canon_product_line(pl: str) -> str:
    if not isinstance(pl, str) or not pl.strip() or pl == EMPTY:
        return EMPTY
    t = pl.strip().lower()
    if t.startswith("auto"):
        return "Auto"
    if t.startswith("prop") or t.startswith("home"):
        return "Property"
    if t.startswith("health"):
        return "Health"
    if t.startswith("travel"):
        return "Travel"
    return pl.strip()

def data_enrichment(field_values: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure suspected_fraud is a canonical 'True/'False
    if "suspected_fraud" in field_values:
        field_values["suspected_fraud"] = _norm_bool_str(field_values.get("suspected_fraud"))

    # Canonicalize product_line or derive from policy_number prefix if missing
    pl = field_values.get("product_line", EMPTY)
    pl = _canon_product_line(pl)
    if (not pl or pl == EMPTY) and isinstance(field_values.get("policy_number"), str):
        pn = field_values["policy_number"].strip()
        if pn.startswith("AU-"):
            pl = "Auto"
        elif pn.startswith("PR-"):
            pl = "Property"
        elif pn.startswith("HE-"):
            pl = "Health"
        elif pn.startswith("TR-"):
            pl = "Travel"
    field_values["product_line"] = pl if pl else EMPTY

    # Derive is_emergency if intention is roadside/emergency
    intention_id = field_values.get("intention_id", "")
    field_values["is_emergency"] = TRUE if intention_id == "roadside_or_emergency_assistance" else FALSE

    return field_values
