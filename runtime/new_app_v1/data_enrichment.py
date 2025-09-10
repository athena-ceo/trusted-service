
from typing import Any
import re

# Mock lookup for tiers by policy number prefix/suffix
_TIER_BY_PREFIX = {
    "BI-PLAT": "platinum",
    "BI-GOLD": "gold",
}

def _infer_tier(policy_number: str | None) -> str:
    if not policy_number:
        return "standard"
    for pref, tier in _TIER_BY_PREFIX.items():
        if policy_number.upper().startswith(pref):
            return tier
    return "standard"

def _parse_refund_amount(text: str | None) -> float | None:
    if not text:
        return None
    # Very loose extraction for numbers like 20, 20.00, €20, 20€
    m = re.search(r"(?:€\s*)?(\d+[\.,]?\d*)\s*€?", text)
    if m:
        try:
            return float(m.group(1).replace(",", "."))
        except:
            return None
    return None

def data_enrichment(field_values: dict[str, Any]):
    """Mutates field_values in place to add derived fields used by the decision engine.
    Mirrors the structure used in sample apps (e.g., conneXion).
    """
    policy_number = field_values.get("policy_number") or ""
    description = field_values.get("description") or ""

    # Derive customer_tier from policy_number
    field_values["customer_tier"] = _infer_tier(policy_number)

    # Simple flags from description (used for prioritization)
    text = description.lower()
    field_values["flag_injury"] = any(w in text for w in ["injury", "injured", "hospital", "blessure", "hôpital"])
    field_values["flag_access_locked"] = any(w in text for w in ["locked out", "cannot login", "impossible de se connecter", "bloqué"])
    field_values["flag_outage"] = any(w in text for w in ["outage", "down", "panne"])

    # Parse a naïve refund amount if mentioned
    amt = _parse_refund_amount(description)
    if amt is not None:
        field_values["refund_amount_eur"] = amt
