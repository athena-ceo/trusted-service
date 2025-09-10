
from typing import Literal, Any
from src.backend.decision.decision import CaseHandlingDecisionEngine, CaseHandlingDecisionOutput, CaseHandlingDecisionInput

# Work basket identifiers
work_basket_claims = "claims"
work_basket_billing = "billing"
work_basket_policy_admin = "policy_admin"
work_basket_tech_portal = "tech_portal"
work_basket_sales_info = "sales_info"
work_basket_complaints = "complaints"
work_basket_fr_support = "fr_support"

# Response templates (email_templates.xlsx ids)
tmpl_fnol_ack = "fnol_ack"
tmpl_proof_self = "proof_of_insurance_self_service"
tmpl_policy_change_self = "policy_change_self_service"
tmpl_refund_small = "refund_small_auto"
tmpl_account_access = "account_access_help"


def _baseline_ack(input: CaseHandlingDecisionInput) -> str:
    # Simple acknowledgement; localized messaging is handled by templates/email or UI.
    intent = input.intention_id.replace("_", " ")
    return f"Thanks! Your request ({intent}) has been received by Best Insurance."


def _bump(priority: Literal["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"]) -> Literal["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"]:
    order = ["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"]
    idx = min(order.index(priority) + 1, len(order)-1)
    return Literal["VERY_LOW","LOW","MEDIUM","HIGH","VERY_HIGH"](__builtins__["str"](order[idx]))  # type: ignore


class DecisionEngineNewApp(CaseHandlingDecisionEngine):

    def _decide(self, input: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
        fv = input.field_values

        # Defaults
        output = CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_baseline_ack(input),
            response_template_id="",
            work_basket="",
            priority="MEDIUM",
            notes=[],
            details={"engine": "new_app"}
        )

        intent = input.intention_id
        lang = (fv.get("preferred_language") or "en").lower()
        tier = fv.get("customer_tier") or "standard"

        # --- Routing by intent ---
        if intent in ["report_claim", "claim_status"]:
            output.work_basket = work_basket_claims
        elif intent == "billing_issue":
            output.work_basket = work_basket_billing
        elif intent in ["policy_change", "policy_cancellation", "proof_of_insurance"]:
            output.work_basket = work_basket_policy_admin
        elif intent == "account_access":
            output.work_basket = work_basket_tech_portal
        elif intent == "product_information":
            output.work_basket = work_basket_sales_info
        elif intent == "complaint_or_feedback":
            output.work_basket = work_basket_complaints
        else:
            output.work_basket = work_basket_complaints  # safe default

        # --- Language override (route to FR basket) ---
        if lang == "fr":
            output.work_basket = work_basket_fr_support
            output.notes.append("Language override: FR")

        # --- Priority rules ---
        urgency = (fv.get("urgency") or "medium").lower()
        base_map = {"low":"LOW","medium":"MEDIUM","high":"HIGH"}
        output.priority = base_map.get(urgency, "MEDIUM")

        if intent == "report_claim" and fv.get("flag_injury"):
            output.priority = "VERY_HIGH"
            output.notes.append("Severe claim: injury detected")

        if intent == "account_access" and fv.get("flag_access_locked"):
            if output.priority in ["LOW","MEDIUM"]:
                output.priority = "HIGH"
            output.notes.append("Access lockout detected")

        # VIP escalation
        if tier in ["gold","platinum"]:
            output.priority = "HIGH" if output.priority == "MEDIUM" else "VERY_HIGH"
            output.notes.append(f"VIP escalation: {tier}")

        # --- Handling/automation rules ---
        if intent == "proof_of_insurance" and fv.get("policy_number"):
            output.handling = "DEFLECTION"
            output.response_template_id = tmpl_proof_self
            output.notes.append("Deflection: self‑service certificate")

        elif intent == "policy_change" and (fv.get("policy_number") and "address" in (fv.get("description") or "").lower()):
            output.handling = "DEFLECTION"
            output.response_template_id = tmpl_policy_change_self
            output.notes.append("Deflection: address/contact change via portal")

        elif intent == "billing_issue":
            amt = fv.get("refund_amount_eur")
            if amt is not None and amt <= 20 and tier != "platinum":
                output.handling = "AUTOMATED"
                output.response_template_id = tmpl_refund_small
                output.notes.append(f"Automated small refund: €{amt}")

        elif intent == "account_access":
            output.response_template_id = tmpl_account_access

        elif intent == "report_claim":
            output.response_template_id = tmpl_fnol_ack

        # Finalize
        return output
