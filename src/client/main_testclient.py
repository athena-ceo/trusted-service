import json
from datetime import date
from time import strptime, struct_time
from typing import Any, Optional

import streamlit as st
from pydantic import BaseModel
from streamlit.delta_generator import DeltaGenerator

from src.client.api_client import ApiClient
from src.client.client_localization import ClientLocalization, frontend_localizations
from src.common.server_api import CaseHandlingRequest, CaseHandlingDetailedResponse, CaseHandlingDecisionInput, CaseHandlingDecisionOutput
from src.common.case_model import CaseModel, Case, CaseField
from src.common.config import SupportedLocale
from src.common.constants import KEY_HIGHLIGHTED_TEXT_AND_FEATURES, KEY_MARKDOWN_TABLE, KEY_ANALYSIS_RESULT, KEY_PROMPT
from src.common.logging import print_red, print_blue

connection_to_api = "direct"


def expander_user(label: str, expanded: bool = False, *, icon: str | None = None) -> DeltaGenerator:
    if icon is None:
        icon = "📋"
    return st.expander(label=f":orange[**{label}**]", expanded=expanded, icon=icon)


def expander_detail(label: str, expanded: bool = False, *, icon: str | None = None) -> DeltaGenerator:
    if icon is None:
        icon = "🔎"
    return st.expander(label=f":blue[{label}]", expanded=expanded, icon=icon)


class Context:
    def __init__(self, api_client: ApiClient, app_id: str, locale: SupportedLocale):
        self.api_client: ApiClient = api_client
        self.app_id: str = app_id
        self.locale: SupportedLocale = locale

        self.frontend_localization: ClientLocalization = frontend_localizations[locale]  # Will fail here if language is not supported

        self.app_name = api_client.get_app_name(app_id, locale)
        self.app_description = api_client.get_app_description(app_id, locale)
        self.sample_message = api_client.get_sample_message(app_id, locale)

        self.case_model: CaseModel = api_client.get_case_model(app_id, locale)
        self.case: Case = Case.create_default_instance(self.case_model)
        self.analysis_result_and_rendering: dict[str, Any] = {}
        self.payload_to_process: str | None = None
        self.case_handling_detailed_response: Optional[CaseHandlingDetailedResponse] = None
        self.stage = 1

    def update_payload_to_process(self):
        pass


def add_case_field_input_widget(case: Case, case_field: CaseField, l12n: ClientLocalization):
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
                                 label_visibility="visible", )

        case.field_values[case_field.id] = d_.strftime(format_python)

    elif case_field.type == "str":

        if case_field.allowed_values:

            # TODO (BUG!) Move after filtering

            # Find index of default value
            # TODO try
            # try
            #     index = case_field.allowed_values.index(case_field.default_value)
            # except ValueError:
            #     index = 0
            index = 0
            for index2, option in enumerate(case_field.allowed_values):
                if option.id == case_field.default_value:
                    index = index2
                    break

            # Filtering according to the condition

            options: list[str] = []
            for option in case_field.allowed_values:
                option_condition = option.condition_python
                try:
                    # Replacing the placeholder with case values in the allowed value condition
                    for field_id in case.field_values:
                        field_value = case.field_values[field_id]
                        option_condition = option_condition.replace("{" + field_id + "}", str(field_value))

                    if eval(option_condition):
                        options.append(option.label)

                except NameError:
                    print_red(f"Error evaluating {option_condition}")
                    options.append(option.label)

            selected_option_label = st.selectbox(label=label,
                                                 options=options,
                                                 index=index,
                                                 help=help_message, )

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
        case.field_values[case_field.id] = st.radio(label=label,
                                                    options=[True, False],
                                                    index=index,
                                                    format_func=lambda v: l12n.label_yes if v else l12n.label_no,
                                                    key=key,
                                                    help=help_message,
                                                    # on_change=update_case_field_bool
                                                    )


def submit_text_for_ia_analysis():
    context: Context = st.session_state.context
    analysis_result_and_rendering = context.api_client.analyze(app_id=context.app_id,
                                                               locale=context.locale,
                                                               field_values=context.case.field_values,
                                                               text=st.session_state.request_description_text_area,
                                                               read_from_cache=st.session_state.read_from_cache,
                                                               llm_config_id=st.session_state.llm_config_id)

    context.analysis_result_and_rendering = analysis_result_and_rendering

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
    context.case_handling_detailed_response = context.api_client.handle_case(context.app_id, context.locale, case_handling_request)

    context.stage = 3


class DecisionPayload(BaseModel):
    decision_input: CaseHandlingDecisionInput
    decision_output: CaseHandlingDecisionOutput


class AppProxy(BaseModel):
    app_id: str
    locales: list[SupportedLocale]
    llm_config_ids: list[str]
    decision_engine_config_ids: list[str]


def populate_apps(api_client: ApiClient):
    app_proxys: list[AppProxy] = []
    app_ids: list[str] = api_client.get_app_ids()
    for app_id in app_ids:
        locales: list[SupportedLocale] = api_client.get_locales(app_id)
        decision_engine_config_ids: list[str] = api_client.get_decision_engine_config_ids(app_id)
        llm_config_ids: list[str] = api_client.get_llm_config_ids(app_id)
        app_proxy = AppProxy(app_id=app_id,
                             locales=locales,
                             llm_config_ids=llm_config_ids,
                             decision_engine_config_ids=decision_engine_config_ids)
        app_proxys.append(app_proxy)
    st.session_state.app_proxys = app_proxys


def app_selected_unselected():
    api_client = st.session_state.api_client
    app_proxy = st.session_state.app_proxy

    if app_proxy is None:
        context = None
        print_red("app_selected_unselected", "context == None")

    else:
        locale = app_proxy.locales[0]
        context = Context(api_client, app_proxy.app_id, locale)
        print_red("app_selected_unselected", app_proxy.app_id, locale)
    st.session_state.context = context


def locale_selected_unselected():
    api_client = st.session_state.api_client
    app_proxy = st.session_state.app_proxy
    locale = st.session_state.locale

    if locale is None:
        context = None
        print_red("locale_selected_unselected", "context == None")

    else:
        context = Context(api_client, app_proxy.app_id, locale)
        print_red("locale_selected_unselected", app_proxy.app_id, locale)
    st.session_state.context = context


def save_cache():
    api_client: ApiClient = st.session_state.api_client
    context: Context = st.session_state.context

    analysis_result: dict[str, Any] = context.analysis_result_and_rendering[KEY_ANALYSIS_RESULT]
    text_analysis_cache: str = json.dumps(analysis_result, ensure_ascii=False, indent=4)
    api_client.save_text_analysis_cache(context.app_id, context.locale, text_analysis_cache)


def reload_apps():
    api_client: ApiClient = st.session_state.api_client
    api_client.reload_apps()
    populate_apps(api_client)


def main_testclient():
    # https://yt3.googleusercontent.com/egw_LrYaDpQ5dUxq_8O1Szx_cP2IqZv2_WlQbsJBoVC5TrqhWmYbVEwSW3qfNwnUlZ6CtesMC8s=s160-c-k-c0x00ffffff-no-rj

    st.logo("images/channels4_profile.jpg", size="small", icon_image=None, link=None)

    with st.sidebar:

        st.write("# Trusted Services")

        columns = st.columns(6, gap=None)

        columns[0].button(
            label="",
            help="Upload app. Not implemented yet; Instead use file transfer and reload apps",
            on_click=None,
            icon=":material/upload:",
            disabled=True, )

        columns[1].button(
            label="",
            help="Download app. Not implemented yet; Instead use file transfer and reload apps",
            on_click=None,
            icon=":material/download:",
            disabled=True, )

        columns[2].button(
            label="",
            help="Reload the apps from the the Trusted Services runtime home directory",  # runtime dir => runtime_home
            on_click=reload_apps,
            icon=":material/directory_sync:", )

        columns[3].button(
            label="",
            help="Trusted Services Assistant",
            on_click=None,
            icon=":material/robot_2:", )

        app_proxys: list[AppProxy] = st.session_state.app_proxys

        app_proxy: AppProxy = st.pills(
            label="App",
            options=app_proxys,
            selection_mode="single",
            default=None,
            format_func=lambda app_proxy: app_proxy.app_id,
            key="app_proxy",
            on_change=app_selected_unselected
        )

        print_red("1")

        if app_proxy is None:
            return

        print_red("2")

        locale: SupportedLocale = st.pills(
            label="Locale",
            options=app_proxy.locales,
            selection_mode="single",
            default=app_proxy.locales[0],
            key="locale",
            on_change=locale_selected_unselected,
        )

        read_from_cache = st.toggle("Read text analysis from cache", value=True, key="read_from_cache")

        llm_config_id: str | None = st.pills(
            label="LLM config",
            options=app_proxy.llm_config_ids,
            selection_mode="single",
            default=app_proxy.llm_config_ids[0],
            key="llm_config_id",
            on_change=None,
            disabled=read_from_cache,
        )

        decision_engine_config_id: str | None = st.pills(
            label="Decision engine config",
            options=app_proxy.decision_engine_config_ids,
            selection_mode="single",
            default=app_proxy.decision_engine_config_ids[0],
            key="decision_engine_config_id",
            on_change=None,
        )
        st.toggle("Details", value=False, key="show_details")

        values_to_check = [locale, read_from_cache, llm_config_id, decision_engine_config_id]
        if [v for v in values_to_check if v is None]:
            return

        context = st.session_state.context

    #  l12n: FrontendLocalization = frontend_localizations[locale]

    l12n = context.frontend_localization

    st.write(f"# {context.app_name}\n{context.app_description}")

    case_model = context.case_model

    case = context.case

    with expander_user(l12n.label_context, expanded=True):

        for case_field in case_model.case_fields:
            if case_field.scope == "CONTEXT":
                add_case_field_input_widget(context.case, case_field, l12n)

    with expander_user(l12n.label_request, expanded=True):

        for case_field in case_model.case_fields:
            if case_field.scope == "CONTEXT":
                continue

            # Show only fields not specific to an intention!
            if not case_field.intention_ids:
                if case_field.show_in_ui:
                    add_case_field_input_widget(context.case, case_field, l12n)

        st.text_area(label=l12n.label_please_describe_your_request,
                     height=330,
                     value=context.sample_message,
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
            tab_prompt, tab_intents, tab_extraction, tab_misc = st.tabs([l12n.label_prompt, l12n.label_intent_scoring, l12n.label_feature_extraction, l12n.label_misc])
            tab_prompt.write(prompt)
            tab_intents.write(markdown_table)
            tab_extraction.html(highlighted_text)
            with tab_misc:
                st.button(
                    label=l12n.label_save_to_cache,
                    on_click=save_cache,
                    icon=":material/save:",
                )

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
                        add_case_field_input_widget(context.case, case_field, l12n)

    # Request text area

    payload = {
        "intention_id": id_of_selected_intention,
        "field_values": case.field_values,
        "highlighted_text_and_features": context.analysis_result_and_rendering["highlighted_text_and_features"],
        "decision_engine_config_id": st.session_state.decision_engine_config_id
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
        with expander_detail(l12n.label_processing_of_the_request):
            rendering_email_to_agent, rendering_email_to_requester = case_handling_detailed_response.case_handling_response.case_handling_report

            # TASK or LOGGING?
            # TASK if agent receives email or ticket
            # LOGGING if AUTO processing or DEFLECTION
            handling = case_handling_detailed_response.case_handling_decision_output.handling
            label_task_or_logging = l12n.label_task if handling == "AGENT" else l12n.label_logging

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
