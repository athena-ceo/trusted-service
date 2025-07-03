import json
from datetime import date, datetime
from time import strptime, struct_time
from typing import Any, Optional, Literal, get_origin, get_args

import streamlit as st
from pydantic import BaseModel
from streamlit.delta_generator import DeltaGenerator

from src.common.api import CaseHandlingRequest, CaseHandlingDetailedResponse, CaseHandlingDecisionInput, CaseHandlingDecisionOutput
from src.common.case_model import CaseModel, Case, CaseField
from src.common.common_configuration import CommonConfiguration, load_common_configuration_from_workbook
from src.common.constants import KEY_HIGHLIGHTED_TEXT_AND_FEATURES, KEY_MARKDOWN_TABLE, KEY_ANALYSIS_RESULT
from src.sample_frontend.api_client import ApiClientDirect, ApiClient, ApiClientHttp
from src.sample_frontend.frontend_configuration import load_frontend_configuration_from_workbook, FrontendConfiguration


def expander_user(label: str, expanded: bool = False, *, icon: str | None = None) -> DeltaGenerator:
    if icon is None:
        icon = "📋"
    return st.expander(label=f":orange[**{label}**]", expanded=expanded, icon=icon)


def expander_detail(label: str, expanded: bool = False, *, icon: str | None = None) -> DeltaGenerator:
    if icon is None:
        icon = "🔎"
    return st.expander(label=f":blue[{label}]", expanded=expanded, icon=icon)


class Context:
    def __init__(self, config_filename: str):
        common_configuration: CommonConfiguration = load_common_configuration_from_workbook(config_filename)
        frontend_configuration: FrontendConfiguration = load_frontend_configuration_from_workbook(config_filename, common_configuration.locale)

        if frontend_configuration.connection_to_api == "rest":
            url = f"http://{common_configuration.rest_api_host}:{common_configuration.rest_api_port}"
            print("URL", url)
            self.api_client: ApiClient = ApiClientHttp(url)
        else:
            self.api_client: ApiClient = ApiClientDirect(config_filename)

        self.case_model: CaseModel = self.api_client.get_case_model()
        self.case: Case = Case.create_default_instance(self.case_model)
        self.analysis_result_and_rendering: dict[str, Any] = {}
        self.payload_to_process: str | None = None
        self.case_handling_detailed_response: Optional[CaseHandlingDetailedResponse] = None
        self.stage = 1

    def update_payload_to_process(self):
        pass


def add_case_field_input_widget(case: Case, case_field: CaseField):
    key = "input_" + case_field.id

    label = case_field.label
    if case_field.mandatory:
        label = label + " __*__"

    value = case.field_values.get(case_field.id)

    help:str = case_field.help
    if help.startswith("https://"):
        help = f"![]({help})"

    if case_field.type == "date":
        # In this case type(value) == str
        format_streamlit = case_field.format
        format_python = (case_field.format
                         .replace("DD", "%d")
                         .replace("MM", "%m")
                         .replace("YYYY", "%Y"))

        st_: struct_time = strptime(value, format_python)
        d_: date = date(st_.tm_year, st_.tm_mon, st_.tm_mday)

        d_: date = st.date_input(label=label,
                                 value=d_,
                                 min_value=None,
                                 max_value=None,
                                 key=None,
                                 help=help,
                                 on_change=None,
                                 args=None, kwargs=None,
                                 format=format_streamlit,
                                 disabled=False,
                                 label_visibility="visible",
                                 )
        print(type(value), value)
        print(type(d_))

        case.field_values[case_field.id] = d_.strftime(format_python)
        print(case.field_values[case_field.id])

    elif case_field.type == "str":

        if case_field.allowed_values:
            index = 0
            for index2, option in enumerate(case_field.allowed_values):
                if option.id == case_field.default_value:
                    index = index2
                    break
            selected_option_label = st.selectbox(label=label,
                                                 options=[option.label for option in case_field.allowed_values],
                                                 index=index,
                                                 help=help,
                                                 )
            selected_options = [option for option in case_field.allowed_values if option.label == selected_option_label]
            selected_option = selected_options[0]
            case.field_values[case_field.id] = selected_option.id

        else:  # TODO Remove update_case_field_str
            def update_case_field_str():
                case.field_values[case_field.id] = st.session_state[key]

            st.text_input(label=label,
                          value=value,
                          key=key,
                          help =  help,
                          on_change=update_case_field_str, )

    elif case_field.type == "bool":

        if value is None:
            index = None
        else:
            index = 0 if value else 1
        val_str = st.radio(label=label,
                           options=["OUI", "NON"],
                           index=index,
                           key=key,
                           help=help,
                           # on_change=update_case_field_bool
                           )
        case.field_values[case_field.id] = val_str == "OUI"


def submit_text_for_ia_analysis():
    context: Context = st.session_state.context
    analysis_result_and_rendering = context.api_client.analyze(context.case.field_values, st.session_state.texte_demande)
    context.analysis_result_and_rendering = analysis_result_and_rendering

    print("CLIENT SIDE")
    print(json.dumps(analysis_result_and_rendering, indent=4))

    # Copy the extracted field values to the case
    for case_field in context.case_model.case_fields:
        if case_field.extraction in ["EXTRACT", "EXTRACT AND HIGHLIGHT"]:
            context.case.field_values[case_field.id] = analysis_result_and_rendering[KEY_ANALYSIS_RESULT][case_field.id]
    st.session_state.context.stage = 2


def submit_case_for_handling():
    context: Context = st.session_state.context

    payload_str = st.session_state.payload
    payload_dict = json.loads(payload_str)
    case_handling_request = CaseHandlingRequest.model_validate(payload_dict)
    context.case_handling_detailed_response = context.api_client.handle_case(case_handling_request)

    context.stage = 3


text1 = """Attestation de prolongation expirée depuis le 11 octobre. 
    Bonjour, 
    
    Je vous sollicite pour le compte de l'un de nos adhérents, Monsieur C C, dont la situation est assez complexe, et dont le numéro de la demande de renouvellement de carte de séjour est le 7500000000000000003.
    
    Il bénéficie actuellement du statut de protection subsidiaire et aimerait se rendre aux obsèques de son père à l'étranger;
    
    Il aimerait déposer une demande de droit d'asile.
    
    Par ailleurs, l'attestation de prolongation d'instruction de Monsieur C est arrivée à expiration depuis le 11 octobre 2024. Aussi, il souhaiterait obtenir une nouvelle attestation pour pouvoir justifier de la régularité de son séjour, dans l'attente de recevoir carte de séjour. 
    
    Sans action dans les prochains jours, il risquera de perdre son travail.
    
    Je vous remercie par avance et vous prie de noter l'urgence. Il risque son emploi, c'est donc très important.
    
    Monsieur C aimerait, par ailleurs, faire une demande d'Asile à la France.
    
    
    Ses coordonnées: 
    Monsieur C C 78500 Sartrouville 07 00 00 00 00 CC@yahoo.com 
    
    Bien à vous.
"""


class DecisionPayload(BaseModel):
    decision_input: CaseHandlingDecisionInput
    decision_output: CaseHandlingDecisionOutput


def streamlit_main(config_filename: str):
    if not hasattr(st.session_state, "context"):
        st.session_state.context = Context(config_filename)
    context = st.session_state.context

    st.write("""
    # DELPHES
    DELPHES est une solution innovante et efficace de pré-traitement et de routage intelligent des demandes adressées par des demandeurs étrangers aux préfectures."
    Il est construit sur le framewotk Athena Démarches en Confiance
    """)

    case_model = context.case_model

    case = context.case

    st.toggle("Montrer les détails", value=False, key="show_details")

    with expander_user("Contexte de la demande", expanded=True):

        for case_field in case_model.case_fields:
            if case_field.scope == "CONTEXT":
                add_case_field_input_widget(context.case, case_field)

    with expander_user("Demande", expanded=True):

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
        on_click=submit_text_for_ia_analysis,
    )

    if context.stage == 1:
        return

    if st.session_state.show_details:
        with expander_detail("Scoring des intentionspar l'IA", expanded=False, icon="✨"):
            analysis_result_and_rendering = context.analysis_result_and_rendering
            markdown_table = analysis_result_and_rendering[KEY_MARKDOWN_TABLE]

            st.write(markdown_table)

        with expander_detail("Extraction d'information par l'IA", expanded=False, icon="✨"):
            analysis_result_and_rendering = context.analysis_result_and_rendering
            highlighted_text = analysis_result_and_rendering[KEY_HIGHLIGHTED_TEXT_AND_FEATURES]

            st.html(highlighted_text)

    with expander_user("Informations complémentaires", expanded=True):
        analysis_result_and_rendering = context.analysis_result_and_rendering
        analysis_result = analysis_result_and_rendering[KEY_ANALYSIS_RESULT]
        scorings = analysis_result["scorings"]

        # Labels of the intentions to show: Either score >= 1 or "OTHER" which exists anyway
        labels = [scoring["intention_label"] for scoring in scorings if
                  scoring["score"] != 0 or scoring["intention_label"] == "AUTRES"]

        label_of_selected_intention = st.radio(label="Confirmer votre demande", options=labels, index=0)
        matching_ids = [scoring["intention_id"] for scoring in scorings if
                        scoring["intention_label"] == label_of_selected_intention]
        if matching_ids:
            id_of_selected_intention = matching_ids[0]

            # Show matching fields
            for case_field in case_model.case_fields:
                # case_field: CaseField = case_field
                # Show fields specific to the selected intention!
                if id_of_selected_intention in case_field.intention_ids:
                    if case_field.show_in_ui:
                        add_case_field_input_widget(context.case, case_field)

    with expander_detail("Requête"):

        payload = {
            "intention_id": id_of_selected_intention,
            "field_values": case.field_values,
            "highlighted_text_and_features": context.analysis_result_and_rendering["highlighted_text_and_features"],
        }

        json_string = json.dumps(payload, indent=4)

        pixels_per_line = 34
        st.text_area(label="JSON string", label_visibility="hidden",
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
        on_click=submit_case_for_handling,
        disabled=False,
    )

    if context.stage == 2:
        return

    case_handling_detailed_response = context.case_handling_detailed_response

    if st.session_state.show_details:
        with expander_detail("Appel au moteur de règles", expanded=False):
            st.write("Input:")
            st.write(case_handling_detailed_response.case_handling_decision_input)
            st.write("Output:")
            st.write(case_handling_detailed_response.case_handling_decision_output)

    st.write(case_handling_detailed_response.case_handling_response.acknowledgement_to_requester)

    if st.session_state.show_details:
        with expander_detail("Traitement de la demande", expanded=False):
            st.html(case_handling_detailed_response.case_handling_response.case_handling_report)
