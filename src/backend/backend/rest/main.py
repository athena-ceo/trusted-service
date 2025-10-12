import inspect
import os
import json
from typing import Optional, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.backend.trusted_services_server import TrustedServicesServer
from src.common.server_api import ServerApi, CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.case_model import CaseModel
from src.common.config import SupportedLocale
from src.common.constants import API_ROUTE_V2
from src.common.logging import print_red


def log_function_call():
    frame = inspect.currentframe().f_back
    func_name = frame.f_code.co_name
    args_info = inspect.getargvalues(frame)
    args_str = ", ".join(f"{arg}={args_info.locals[arg]!r}" for arg in args_info.args)
    print(f"{func_name}({args_str})")


class FastAPI2(FastAPI):

    def __init__(self):
        app_env = os.getenv("APP_ENV", "local")

        if app_env == "production":
            super().__init__(
                title="Trusted Services API",
                docs_url="/docs",
                openapi_url="/openapi.json",
                root_path="/trusted-services-api"
            )
        else:  # local
            super().__init__(
                title="Trusted Services API",
                docs_url="/docs",
                openapi_url="/openapi.json"
            )
        self.server_api: Optional[ServerApi] = None

    def init(self,
             connection_configuration,
             runtime_directory):

        # self.add_middleware(
        #     CORSMiddleware,
        #     allow_origins=[connection_configuration.client_url, "http://localhost:5005"],
        #     allow_credentials=True,
        #     allow_methods=["*"],
        #     allow_headers=["*"],
        # )

        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # allow any origin
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.server_api: ServerApi = TrustedServicesServer(runtime_directory)


app: FastAPI2 = FastAPI2()


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.post(API_ROUTE_V2 + "/reload_apps")
async def reload_apps():
    print_red("*** reload_apps ***")
    log_function_call()
    return app.server_api.reload_apps()


@app.get(API_ROUTE_V2 + "/app_ids", response_model=list[str], summary="Get the ids of all apps defined")
async def get_app_ids() -> list[str]:
    log_function_call()
    return app.server_api.get_app_ids()


@app.get(API_ROUTE_V2 + "/apps/{app_id}/locales", response_model=list[str])
async def get_locales(app_id: str) -> list[str]:
    log_function_call()
    return app.server_api.get_locales(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/llm_config_ids", response_model=list[str])
async def get_llm_config_ids(app_id: str) -> list[str]:
    log_function_call()
    return app.server_api.get_llm_config_ids(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/decision_engine_config_ids", response_model=list[str])
async def get_decision_engine_config_ids(app_id: str) -> list[str]:
    log_function_call()
    return app.server_api.get_decision_engine_config_ids(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{locale}/app_name")
async def get_app_name(app_id: str, locale: SupportedLocale) -> str:
    log_function_call()
    return app.server_api.get_app_name(app_id=app_id, locale=locale)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{locale}/app_description")
async def get_app_description(app_id: str, locale: SupportedLocale) -> str:
    log_function_call()
    return app.server_api.get_app_description(app_id=app_id, locale=locale)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{locale}/sample_message")
async def get_sample_message(app_id: str, locale: SupportedLocale) -> str:
    log_function_call()
    return app.server_api.get_sample_message(app_id=app_id, locale=locale)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{locale}/case_model")
async def get_case_model(app_id: str, locale: SupportedLocale) -> CaseModel:
    log_function_call()
    return app.server_api.get_case_model(app_id=app_id, locale=locale)


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{locale}/analyze")
async def analyze(app_id: str, locale: SupportedLocale, field_values: str, text: str, read_from_cache: bool, llm_config_id: str):
    log_function_call()
    field_values2 = json.loads(field_values)
    return app.server_api.analyze(app_id=app_id, locale=locale, field_values=field_values2, text=text, read_from_cache=read_from_cache, llm_config_id=llm_config_id)


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{locale}/save_text_analysis_cache")
async def save_text_analysis_cache(app_id: str, locale: SupportedLocale, text_analysis_cache: str):
    log_function_call()
    return app.server_api.save_text_analysis_cache(app_id, locale, text_analysis_cache)


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{locale}/handle_case")
async def handle_case(app_id: str, locale: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
    log_function_call()
    return app.server_api.handle_case(app_id=app_id, locale=locale, request=request)


API_ROUTE = "/api/v1"
# API_ROUTE = "/delphes-api/api/v1"


@app.post(f"{API_ROUTE}/analyze", tags=["Services"])
async def analyze_v1(data: dict) -> dict[str, Any]:
    # Extract the field values from the POST request body
    field_values: dict[str, Any] = data.get("field_values", "{}")

    # Extract the message from the POST request body
    text: str = data.get("text", "")

    lang: SupportedLocale = data.get("lang", "fr").lower()

    print("********************************** analyser_demande **********************************")
    return app.server_api.analyze(app_id="delphes", locale=lang, field_values=field_values, text=text, read_from_cache=False, llm_config_id="tests")


@app.post(f"{API_ROUTE}/process_request", tags=["Services"])
async def handle_case_v1(data: dict):
    # Extract the case request object from the POST request body
    case_request = data.get("case_request", "{}")
    if isinstance(case_request, dict):
        if "decision_engine_config_id" not in case_request:
            case_request["decision_engine_config_id"] = "tests"
        case_request = CaseHandlingRequest(**case_request)

    lang: SupportedLocale = data.get("lang", "fr").lower()

    print("********************************** handle_case_v1 **********************************")
    return app.server_api.handle_case(app_id="delphes", locale=lang, request=case_request)
