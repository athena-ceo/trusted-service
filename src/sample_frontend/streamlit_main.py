import json
from datetime import date
from time import strptime, struct_time
from typing import Any, Optional

import streamlit as st
from pydantic import BaseModel
from streamlit.delta_generator import DeltaGenerator

from src.common.api import CaseHandlingRequest, CaseHandlingDetailedResponse, CaseHandlingDecisionInput, CaseHandlingDecisionOutput
from src.common.case_model import CaseModel, Case, CaseField
from src.common.common_configuration import CommonConfiguration, load_common_configuration_from_workbook
from src.common.constants import KEY_HIGHLIGHTED_TEXT_AND_FEATURES, KEY_MARKDOWN_TABLE, KEY_ANALYSIS_RESULT, KEY_PROMPT
from src.sample_frontend.api_client import ApiClientDirect, ApiClient, ApiClientHttp
from src.sample_frontend.frontend_configuration import load_frontend_configuration_from_workbook, FrontendConfiguration
from src.sample_frontend.frontend_localization import FrontendLocalization, frontend_localizations


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

        self.locale = common_configuration.locale

        self.frontend_localization: FrontendLocalization = frontend_localizations[self.locale]  # Will fail here if language is not supported

        if frontend_configuration.connection_to_api == "rest":
            url = f"http://{common_configuration.rest_api_host}:{common_configuration.rest_api_port}"
            # print("URL", url)
            self.api_client: ApiClient = ApiClientHttp(url)
        else:
            self.api_client: ApiClient = ApiClientDirect(config_filename)

        self.app_name = self.api_client.get_app_name()
        self.app_description = self.api_client.get_app_description()

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

    help_message: str = case_field.help
    if help_message.startswith("https://"):
        help_message = f"![]({help_message})"

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
                                 help=help_message,
                                 on_change=None,
                                 args=None, kwargs=None,
                                 format=format_streamlit,
                                 disabled=False,
                                 label_visibility="visible",
                                 )
        # print(type(value), value)
        # print(type(d_))

        case.field_values[case_field.id] = d_.strftime(format_python)
        # print(case.field_values[case_field.id])

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
                                                 help=help_message,
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
                          help=help_message,
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
                           help=help_message,
                           # on_change=update_case_field_bool
                           )
        case.field_values[case_field.id] = val_str == "OUI"


def submit_text_for_ia_analysis():
    context: Context = st.session_state.context
    analysis_result_and_rendering = context.api_client.analyze(context.case.field_values, st.session_state.request_description_text_area)
    context.analysis_result_and_rendering = analysis_result_and_rendering

    # print("CLIENT SIDE")
    # print(json.dumps(analysis_result_and_rendering, indent=4))

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


sample1_en = """Hello,

I am writing on behalf of one of our members, Mr C C, whose case is rather complex and whose residence‑permit renewal application number (numéro de la demande de renouvellement de carte de séjour) is 7500000000000000003.

He currently holds subsidiary protection status and would like to travel to his home country, on a temporary and exceptional basis, to attend his father’s funeral.

He would also like to submit an asylum application.

In addition, Mr C’s processing‑extension certificate expired on 11 October 2024. He therefore wishes to obtain a new certificate so he can prove the legality of his stay while awaiting his residence permit.

Without action in the next few days, he risks losing his job.

Thank you in advance for your attention; please note the urgency—his employment is at stake, so this matter is very important.

Mr C would furthermore like to file an asylum request with France."""

sample1_fr = """Bonjour, 

Je vous sollicite pour le compte de l'un de nos adhérents, Monsieur C C, dont la situation est assez complexe, et dont le numéro de la demande de renouvellement de carte de séjour est le 7500000000000000003.

Il bénéficie actuellement du statut de protection subsidiaire et aimerait se rendre dans son pays de façon temporaire et exceptionnelle pour assister aux obsèques de son père.

Il aimerait déposer une demande de droit d'asile.

Par ailleurs, l'attestation de prolongation d'instruction de Monsieur C est arrivée à expiration depuis le 11 octobre 2024. Aussi, il souhaiterait obtenir une nouvelle attestation pour pouvoir justifier de la régularité de son séjour, dans l'attente de recevoir carte de séjour. 

Sans action dans les prochains jours, il risquera de perdre son travail.

Je vous remercie par avance et vous prie de noter l'urgence. Il risque son emploi, c'est donc très important.

Monsieur C aimerait, par ailleurs, faire une demande d'Asile à la France."""


class DecisionPayload(BaseModel):
    decision_input: CaseHandlingDecisionInput
    decision_output: CaseHandlingDecisionOutput


def streamlit_main(config_filename: str):
    if not hasattr(st.session_state, "context"):
        st.session_state.context = Context(config_filename)
    context = st.session_state.context
    l12n = context.frontend_localization

    st.write(f"# {context.app_name}\n{context.app_description}")

    case_model = context.case_model

    case = context.case

    st.toggle(l12n.label_show_details, value=False, key="show_details")

    with expander_user(l12n.label_context, expanded=True):

        for case_field in case_model.case_fields:
            if case_field.scope == "CONTEXT":
                add_case_field_input_widget(context.case, case_field)

    with expander_user(l12n.label_request, expanded=True):

        for case_field in case_model.case_fields:
            if case_field.scope == "CONTEXT":
                continue

            # Show only fields not specific to an intention!
            if not case_field.intention_ids:
                if case_field.show_in_ui:
                    add_case_field_input_widget(context.case, case_field)

        # IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
        # Add here support for new languages
        sample = sample1_en if context.locale == "en" else sample1_fr

        st.text_area(label=l12n.label_please_describe_your_request,
                     height=330,
                     value=sample,
                     key="request_description_text_area", )

    st.button(
        label=l12n.label_next_step,
        on_click=submit_text_for_ia_analysis,
        icon="➡️"
    )

    if context.stage == 1:
        return

    if st.session_state.show_details:
        analysis_result_and_rendering = context.analysis_result_and_rendering
        prompt = analysis_result_and_rendering[KEY_PROMPT]
        markdown_table = analysis_result_and_rendering[KEY_MARKDOWN_TABLE]
        highlighted_text = analysis_result_and_rendering[KEY_HIGHLIGHTED_TEXT_AND_FEATURES]

        with expander_detail(l12n.label_text_analysis):
            tab_prompt, tab_intents, tab_extraction = st.tabs([l12n.label_prompt, l12n.label_intent_scoring, l12n.label_feature_extraction])
            tab_prompt.write(prompt)
            tab_intents.write(markdown_table)
            tab_extraction.html(highlighted_text)

    with expander_user(l12n.label_additional_information, expanded=True):
        analysis_result_and_rendering = context.analysis_result_and_rendering
        analysis_result = analysis_result_and_rendering[KEY_ANALYSIS_RESULT]
        scorings = analysis_result["scorings"]

        # Labels of the intentions to show: Either score >= 1 or other which exists anyway
        labels = [scoring["intention_label"] for scoring in scorings if scoring["score"] != 0]

        label_of_selected_intention = st.radio(label=l12n.label_confirm_your_request, options=labels, index=0)
        matching_ids = [scoring["intention_id"] for scoring in scorings if scoring["intention_label"] == label_of_selected_intention]
        if matching_ids:
            id_of_selected_intention = matching_ids[0]

            # Show matching fields
            for case_field in case_model.case_fields:
                if id_of_selected_intention in case_field.intention_ids:
                    if case_field.show_in_ui:
                        add_case_field_input_widget(context.case, case_field)

    # Request text area

    payload = {
        "intention_id": id_of_selected_intention,
        "field_values": case.field_values,
        "highlighted_text_and_features": context.analysis_result_and_rendering["highlighted_text_and_features"],
    }

    json_string = json.dumps(payload, indent=4)

    pixels_per_line = 34

    if st.session_state.show_details:

        with expander_detail(l12n.label_request):
            st.text_area(label="JSON string", label_visibility="hidden",
                         value=json_string,
                         height=len(json_string.splitlines()) * pixels_per_line,
                         key="payload",
                         disabled=False,
                         )
    else:

        with st.expander(label="", expanded=False):
            st.text_area(label="JSON string", label_visibility="hidden",
                         value=json_string,
                         height=len(json_string.splitlines()) * pixels_per_line,
                         key="payload",
                         disabled=True,
                         )

    st.button(
        label=l12n.label_submit,
        on_click=submit_case_for_handling,
        icon="📤",
    )

    if context.stage == 2:
        return

    case_handling_detailed_response = context.case_handling_detailed_response

    if st.session_state.show_details:
        with expander_detail(l12n.label_text_analysis):
            rendering_email_to_agent, rendering_email_to_requester = case_handling_detailed_response.case_handling_response.case_handling_report

            # TASK or LOGGING?
            handling = case_handling_detailed_response.case_handling_decision_output.handling
            label_task_or_logging = l12n.label_task if handling=="AGENT" else l12n.label_logging

            tab_labels = [l12n.label_rule_engine_invocation, label_task_or_logging]
            if rendering_email_to_requester:
                tab_labels.append(l12n.label_proposed_response)
            tabs = st.tabs(tab_labels)

            tabs[0].write("Input:")
            tabs[0].write(case_handling_detailed_response.case_handling_decision_input)
            tabs[0].write("Output:")
            tabs[0].write(case_handling_detailed_response.case_handling_decision_output)

            tabs[1].html(rendering_email_to_agent)

            if rendering_email_to_requester:
                tabs[2].html(rendering_email_to_requester)

    st.write(case_handling_detailed_response.case_handling_response.acknowledgement_to_requester)
