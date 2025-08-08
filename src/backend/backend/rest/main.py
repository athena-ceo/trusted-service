import inspect
import json
from typing import Optional, Any, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.backend.trusted_services_server import TrustedServicesServer
from src.common.api import Api, CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.case_model import CaseModel
from src.common.configuration import SupportedLocale
from src.common.constants import API_ROUTE_V2


def log_function_call():
    frame = inspect.currentframe().f_back
    func_name = frame.f_code.co_name
    args_info = inspect.getargvalues(frame)
    args_str = ", ".join(f"{arg}={args_info.locals[arg]!r}" for arg in args_info.args)
    print(f"{func_name}({args_str})")


class FastAPI2(FastAPI):

    def __init__(self):
        super().__init__()
        self.api: Optional[Api] = None

    def init(self, connection_configuration, appdef_filenames: list[str]):
        self.add_middleware(
            CORSMiddleware,
            allow_origins=[connection_configuration.client_url, "http://localhost:5005"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.api: Api = TrustedServicesServer(appdef_filenames)


app: FastAPI2 = FastAPI2()


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get(API_ROUTE_V2 + "/app_ids", response_model=list[str], summary="Get the ids of all apps defined")
async def get_app_ids() -> list[str]:
    log_function_call()
    return app.api.get_app_ids()


@app.get(API_ROUTE_V2 + "/apps/{app_id}/locales", response_model=list[str])
async def get_locales(app_id: str) -> list[str]:
    log_function_call()
    return app.api.get_locales(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/llm_config_ids", response_model=list[str])
async def get_llm_config_ids(app_id: str) -> list[str]:
    log_function_call()
    return app.api.get_llm_config_ids(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/decision_engine_config_ids", response_model=list[str])
async def get_decision_engine_config_ids(app_id: str) -> list[str]:
    log_function_call()
    return app.api.get_decision_engine_config_ids(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{loc}/app_name")
async def get_app_name(app_id: str, loc: SupportedLocale) -> str:
    log_function_call()
    return app.api.get_app_name(app_id=app_id, loc=loc)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{loc}/app_description")
async def get_app_description(app_id: str, loc: SupportedLocale) -> str:
    log_function_call()
    return app.api.get_app_description(app_id=app_id, loc=loc)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{loc}/sample_message")
async def get_sample_message(app_id: str, loc: SupportedLocale) -> str:
    log_function_call()
    return app.api.get_sample_message(app_id=app_id, loc=loc)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{loc}/case_model")
async def get_case_model(app_id: str, loc: SupportedLocale) -> CaseModel:
    log_function_call()
    return app.api.get_case_model(app_id=app_id, loc=loc)


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{loc}/analyze")
async def analyze(app_id: str, loc: SupportedLocale, field_values: str, text: str, read_from_cache: bool):
    log_function_call()
    field_values2 = json.loads(field_values)
    return app.api.analyze(app_id=app_id, loc=loc, field_values=field_values2, text=text, read_from_cache=read_from_cache)


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{loc}/save_text_analysis_cache")
async def save_text_analysis_cache(app_id: str, loc: SupportedLocale, text_analysis_cache: str):
    log_function_call()
    return app.api.save_text_analysis_cache(app_id, loc, text_analysis_cache)


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{loc}/handle_case")
async def handle_case(app_id: str, loc: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
    log_function_call()
    return app.api.handle_case(app_id=app_id, loc=loc, request=request)


# API_ROUTE = "/api/v1"
API_ROUTE = "/delphes-api/api/v1"

print(f"{API_ROUTE}/analyze")
print("***")


@app.post(f"{API_ROUTE}/analyze", tags=["Services"])
async def analyze_v1(data: dict) -> dict[str, Any]:
    # Extract the field values from the POST request body
    field_values: dict[str, Any] = data.get("field_values", "{}")

    # Extract the message from the POST request body
    text: str = data.get("text", "")

    print("********************************** analyser_demande **********************************")
    return app.api.analyze(app_id="delphes", loc="fr", field_values=field_values, text=text, read_from_cache=False)


@app.post(f"{API_ROUTE}/process_request", tags=["Services"])
async def handle_case_v1(data: dict):
    # Extract the case request object from the POST request body
    case_request = data.get("case_request", "{}")
    if isinstance(case_request, dict):
        if "decision_engine_config_id" not in case_request:
            case_request["decision_engine_config_id"] = "tests"
        case_request = CaseHandlingRequest(**case_request)

    print("********************************** handle_case_v1 **********************************")
    return app.api.handle_case(app_id="delphes", loc="fr", request=case_request)
