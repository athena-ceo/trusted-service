import json
from typing import Any, Optional

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from common.src.api import CaseHandlingRequest, CaseHandlingResponse
from common.src.case_model import CaseModel, Case, CaseField
from common.src.constants import KEY_HIGHLIGHTED_TEXT_AND_FEATURES, KEY_MARKDOWN_TABLE, KEY_ANALYSIS_RESULT
from frontend.src.api_client import ApiClientDirect, ApiClient


def expander2(label: str, expanded: bool = False, *, icon: str | None = None) -> DeltaGenerator:
    return st.expander(label=f":orange[**{label}**]", expanded=expanded, icon=icon)


class Context:
    def __init__(self):
        self.stage = 1
        # self.api_client: ApiClient = ApiClientHttp()
        self.api_client: ApiClient = ApiClientDirect()

        self.case_model: CaseModel = self.api_client.get_case_model()
        self.case: Case = Case.create_default_instance(self.case_model)
        self.analysis_result_and_rendering: dict[str, Any] = {}
        self.processing_response: Optional[CaseHandlingResponse] = None


def add_case_field_input_widget(case: Case, case_field: CaseField):
    key = "input_" + case_field.id

    value = case.field_values.get(case_field.id)

    if case_field.get_type() is str:

        def update_case_field_str():
            case.field_values[case_field.id] = st.session_state[key]

        st.text_input(label=case_field.label,
                      value=value,
                      key=key,
                      on_change=update_case_field_str, )

    elif case_field.get_type() is bool:
        def update_case_field_bool():
            case.field_values[case_field.id] = st.session_state[key] == "OUI"

        if value is None:
            index = None
        else:
            index = 0 if value else 1
        st.radio(label=case_field.label,
                 options=["OUI", "NON"],
                 index=index,
                 key=key,
                 on_change=update_case_field_bool)


def submit_for_text_analysis():
    context: Context = st.session_state.context
    analysis_result_and_rendering = context.api_client.analyze_and_render(context.case.field_values, st.session_state.texte_demande)
    context.analysis_result_and_rendering = analysis_result_and_rendering

    # Copy the extracted field values to the case
    for case_field in context.case_model.case_fields:
        if case_field.extraction in ["EXTRACT", "EXTRACT AND HIGHLIGHT"]:
            context.case.field_values[case_field.id] = analysis_result_and_rendering[KEY_ANALYSIS_RESULT][case_field.id]
    st.session_state.context.stage = 2


def submit_request():
    context: Context = st.session_state.context

    payload_str = st.session_state.payload
    payload_dict = json.loads(payload_str)
    processing_request = CaseHandlingRequest.model_validate(payload_dict)
    context.processing_response = context.api_client.handle_case(processing_request)

    context.stage = 3


text1 = """Attestation de prolongation expirée depuis le 11 octobre. 
    Bonjour, 
    Je vous sollicite pour le compte de l'un de nos adhérents, Monsieur C C, dont le numéro de la demande de renouvellement de carte de séjour est le 7500000000000000003. En effet, l'attestation de prolongation d'instruction de Monsieur C est arrivée à expiration depuis le 11 octobre 2024. Aussi, il souhaiterait obtenir une nouvelle attestation pour pouvoir justifier de la régularité de son séjour, dans l'attente de recevoir carte de séjour. 
    
    Sans action dans les prochains jours, il risquera de perdre son travail.
    
    Je vous remercie par avance et vous prie de noter l'urgence. Il risque son emploi, c'est donc très important.
    
    
    Ses coordonnées: 
    Monsieur C C 78500 Sartrouville 07 00 00 00 00 CC@yahoo.com 
    
    Bien à vous.
"""

text2 = """Bonjour,

J'ai effectué la démarche en ligne sur ANEF pour le renouvellement de mon titre séjour - passeport talent le 09-08-2023. j'ai reçu l'attestation de prolongation directement après l'expiration de mon titre de séjour. cette dernière à été renouvelée le 29-02-2024 et expirée le 28/05/2024.
Mais jusqu'à ce jour je n'ai pas reçu une nouvelle API sachant que l’état d'avancement est toujours en instruction.alors que selon l'article R431-15-1 du code de l'entrée et du séjour des étrangers et du droit d'asile : "... Lorsque l'instruction se prolonge, en raison de circonstances particulières, au-delà de la date d'expiration de l'attestation, celle-ci est renouvelée aussi longtemps que le préfet n'a pas statué sur la demande." par conséquent, j'ai envoyé plusieurs courriel de relance à la préfecture mais sans réponse.
Mon contrat de travail et suspendu et dans l'impossibilité de fournir ce document dans les plus brefs délais, je verrai malheureusement mon contrat de travail résilié.
"""


text1 = """Attestation de prolongation expirée depuis le 11 octobre. 
    Bonjour, 
    Je vous sollicite pour le compte de l'un de nos adhérents, Monsieur C C, dont le numéro de la demande de renouvellement de carte de séjour est le 7500000000000000003. En effet, l'attestation de prolongation d'instruction de Monsieur C est arrivée à expiration depuis le 11 octobre 2024. Aussi, il souhaiterait obtenir une nouvelle attestation pour pouvoir justifier de la régularité de son séjour, dans l'attente de recevoir carte de séjour. 
    
    Sans action dans les prochains jours, il risquera de perdre son travail.
    
    Je vous remercie par avance et vous prie de noter l'urgence. Il risque son emploi, c'est donc très important.
    
    Monsieur C aimerait, par ailleurs, faire une demande d'Asile à la France.
    
    
    Ses coordonnées: 
    Monsieur C C 78500 Sartrouville 07 00 00 00 00 CC@yahoo.com 
    
    Bien à vous.
"""


def streamlit_main():
    if not hasattr(st.session_state, "context"):
        st.session_state.context = Context()
    context = st.session_state.context

    st.write("""
    # DELPHES
    DELPHES est une solution innovante et efficace de pré-traitement et de routage intelligent des demandes adressées par des demandeurs étrangers aux préfectures."
    Il est construit sur le framewotk Athena Démarches en Confiance
    """)

    case_model = context.case_model

    case = context.case

    st.toggle("Montrer les détails", value=False, key="show_details")

    with expander2("Contexte de la demande", expanded=True):

        for case_field in case_model.case_fields:
            if case_field.scope == "CONTEXT":
                add_case_field_input_widget(context.case, case_field)

    with expander2("Demande", expanded=True):

        for case_field in case_model.case_fields:
            if case_field.scope == "CONTEXT":
                continue

            # Show only fields not specific to an intention!
            if not case_field.intention_ids:
                if case_field.show_in_ui:
                    add_case_field_input_widget(context.case, case_field)

        st.text_area(label="Veuillez décrire votre demande",
                     height=330,
                     value=text1,
                     key="texte_demande", )

    st.button(
        label=f"Etape suivante",
        on_click=submit_for_text_analysis,
    )

    if context.stage == 1:
        return

    if st.session_state.show_details:
        with expander2("Scoring des intentionspar l'IA", expanded=False, icon="✨"):
            analysis_result_and_rendering = context.analysis_result_and_rendering
            markdown_table = analysis_result_and_rendering[KEY_MARKDOWN_TABLE]

            st.write(markdown_table)

        with expander2("Extraction d'information par l'IA", expanded=False, icon="✨"):
            analysis_result_and_rendering = context.analysis_result_and_rendering
            highlighted_text = analysis_result_and_rendering[KEY_HIGHLIGHTED_TEXT_AND_FEATURES]

            st.html(highlighted_text)

    with expander2("Informations complémentaires", expanded=True):
        analysis_result_and_rendering = context.analysis_result_and_rendering
        analysis_result = analysis_result_and_rendering[KEY_ANALYSIS_RESULT]
        scorings = analysis_result["scorings"]
        labels = [scoring["intention_label"] for scoring in scorings if
                  scoring["score"] != 0 or scoring["intention_label"] == "AUTRES"]
        label_of_selected_intention = st.radio(label="Confirmer votre demande", options=labels, index=0)
        matching_ids = [scoring["intention_id"] for scoring in scorings if
                        scoring["intention_label"] == label_of_selected_intention]
        if matching_ids:
            id_of_selected_intention = matching_ids[0]
            for case_field in case_model.case_fields:
                case_field: CaseField = case_field
                # Show fields specific to the selected intention!
                if id_of_selected_intention in case_field.intention_ids:
                    if case_field.show_in_ui:
                        add_case_field_input_widget(context.case, case_field)

    with expander2("Requête"):

        case_field_values_to_send_to_decision_engine: dict[str, Any] = {}

        for case_field in case_model.case_fields:
            # if case_field.send_to_decision_engine:
            case_field_values_to_send_to_decision_engine[case_field.id] = case.field_values[case_field.id]

        payload = {
            "intention_id": id_of_selected_intention,
            "field_values": case_field_values_to_send_to_decision_engine,
            "highlighted_text_and_features": context.analysis_result_and_rendering["highlighted_text_and_features"],
        }

        json_string = json.dumps(payload, indent=4)

        pixels_per_line = 34
        st.text_area("JSON Payload",
                     value=json_string,
                     height=len(json_string.splitlines()) * pixels_per_line,
                     max_chars=None,
                     key="payload",
                     help=None,
                     on_change=None,
                     args=None,
                     kwargs=None,
                     placeholder=None,
                     disabled=False,
                     )

    st.button(
        label=f"Soumettre votre demande",
        on_click=submit_request,
        disabled=False,
    )

    if context.stage == 2:
        return

    processing_response = context.processing_response

    st.write(processing_response.acknowledgement_to_requester)

    if st.session_state.show_details:
        with expander2("Traitement de la demande", expanded=False):
            st.html(processing_response.case_handling_report)
