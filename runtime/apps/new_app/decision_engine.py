from typing import Any, Literal, Dict
from pydantic import BaseModel

class CaseHandlingDecisionInput(BaseModel):
    intention_id: str
    field_values: Dict[str, Any]

class CaseHandlingDecisionOutput(BaseModel):
    handling: Literal["AUTOMATED", "AGENT", "DEFLECTION"]
    acknowledgement_to_requester: str
    response_template_id: str
    work_basket: str
    priority: Literal["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
    notes: list[str]
    details: Any = None

# Proposed work baskets (email queues)
WORK_BASKETS = {
    "emergency": "emergency@bestinsurance.com",
    "fraud": "fraud@bestinsurance.com",
    "claims-auto": "claims.auto@bestinsurance.com",
    "claims-property": "claims.property@bestinsurance.com",
    "billing": "billing@bestinsurance.com",
    "policy-service": "policy.service@bestinsurance.com",
    "retention": "retention@bestinsurance.com",
    "sales": "sales@bestinsurance.com",
    "complaints": "complaints@bestinsurance.com",
    "general": "support@bestinsurance.com",
}

def _ack(template_key: str) -> str:
    texts = {
        "emergency_ack": "Thanks for reaching Best Insurance. We've flagged your request as urgent and are connecting you with an agent right away.",
        "fraud_ack": "Thanks for reporting suspected fraud. Our specialized team will investigate and contact you shortly.",
        "claim_auto_ack": "Your auto claim has been received. An agent will review and follow up soon.",
        "claim_property_ack": "Your property claim has been received. An agent will review and follow up soon.",
        "billing_ack": "We've received your billing request. We'll review and get back to you.",
        "policy_service_ack": "We've received your policy service request. We'll process it and let you know if we need anything else.",
        "documents_auto_ack": "Your document request was received. We'll send the documents to your email on file.",
        "cancellation_ack": "We received your cancellation request. A specialist will contact you to complete it.",
        "quote_ack": "Thanks for your interest. A licensed agent will prepare your quote.",
        "complaint_ack": "We're sorry to hear this. Your complaint has been logged and escalated to a specialist.",
        "general_ack": "Thanks for contacting Best Insurance. We've received your message.",
    }
    return texts.get(template_key, "Thanks for contacting Best Insurance. We received your message.")

def decide(inp: CaseHandlingDecisionInput) -> CaseHandlingDecisionOutput:
    fv = inp.field_values or {}
    intention = (inp.intention_id or "").strip()

    product_line = (fv.get("product_line") or "").strip()
    suspected_fraud = str(fv.get("suspected_fraud", "")).strip().lower() in {"'true", "true"}
    is_emergency = str(fv.get("is_emergency", "")).strip().lower() in {"'true", "true"}

    # R1: Emergency
    if intention == "roadside_or_emergency_assistance" or is_emergency:
        return CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_ack("emergency_ack"),
            response_template_id="emergency_ack",
            work_basket="emergency",
            priority="VERY_HIGH",
            notes=["Emergency assistance routing"],
            details={"work_basket_email": WORK_BASKETS["emergency"]},
        )

    # R2: Fraud
    if intention == "report_fraud" or suspected_fraud:
        return CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_ack("fraud_ack"),
            response_template_id="fraud_ack",
            work_basket="fraud",
            priority="VERY_HIGH",
            notes=["Suspected fraud routing"],
            details={"work_basket_email": WORK_BASKETS["fraud"]},
        )

    # R3: New claim - Auto
    if intention == "file_claim" and product_line.lower().startswith("auto"):
        return CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_ack("claim_auto_ack"),
            response_template_id="claim_auto_ack",
            work_basket="claims-auto",
            priority="HIGH",
            notes=["Auto claim routing"],
            details={"work_basket_email": WORK_BASKETS["claims-auto"]},
        )

    # R4: New claim - Property
    if intention == "file_claim" and product_line.lower().startswith("prop"):
        return CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_ack("claim_property_ack"),
            response_template_id="claim_property_ack",
            work_basket="claims-property",
            priority="HIGH",
            notes=["Property claim routing"],
            details={"work_basket_email": WORK_BASKETS["claims-property"]},
        )

    # R5: Billing
    if intention == "billing_issue":
        return CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_ack("billing_ack"),
            response_template_id="billing_ack",
            work_basket="billing",
            priority="MEDIUM",
            notes=["Billing issue routing"],
            details={"work_basket_email": WORK_BASKETS["billing"]},
        )

    # R6: Policy service
    if intention in {"change_personal_details", "request_document"}:
        automated = (intention == "request_document")
        return CaseHandlingDecisionOutput(
            handling="AUTOMATED" if automated else "AGENT",
            acknowledgement_to_requester=_ack("documents_auto_ack" if automated else "policy_service_ack"),
            response_template_id="documents_auto_ack" if automated else "policy_service_ack",
            work_basket="policy-service",
            priority="LOW",
            notes=["Automated docs" if automated else "Policy service routing"],
            details={"work_basket_email": WORK_BASKETS["policy-service"]},
        )

    # R7: Cancellation/Retention
    if intention == "policy_cancellation":
        return CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_ack("cancellation_ack"),
            response_template_id="cancellation_ack",
            work_basket="retention",
            priority="HIGH",
            notes=["Retention routing"],
            details={"work_basket_email": WORK_BASKETS["retention"]},
        )

    # R8: Quote
    if intention == "quote_request":
        return CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_ack("quote_ack"),
            response_template_id="quote_ack",
            work_basket="sales",
            priority="MEDIUM",
            notes=["Sales/quote routing"],
            details={"work_basket_email": WORK_BASKETS["sales"]},
        )

    # R9: Complaint
    if intention == "complaint":
        return CaseHandlingDecisionOutput(
            handling="AGENT",
            acknowledgement_to_requester=_ack("complaint_ack"),
            response_template_id="complaint_ack",
            work_basket="complaints",
            priority="HIGH",
            notes=["Complaint escalation"],
            details={"work_basket_email": WORK_BASKETS["complaints"]},
        )

    # Fallback: General
    return CaseHandlingDecisionOutput(
        handling="AGENT",
        acknowledgement_to_requester=_ack("general_ack"),
        response_template_id="general_ack",
        work_basket="general",
        priority="LOW",
        notes=["General routing"],
        details={"work_basket_email": WORK_BASKETS["general"]},
    )
