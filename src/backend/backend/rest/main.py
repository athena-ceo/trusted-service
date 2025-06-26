import json
from typing import Optional, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.backend.application import Application
from src.common.api import Api, CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.case_model import CaseModel
from src.common.common_configuration import load_common_configuration_from_workbook, CommonConfiguration


class FastAPI2(FastAPI):

    def __init__(self):
        super().__init__()
        self.api: Optional[Api] = None

    def set_config_filename(self, config_filename):
        common_configuration: CommonConfiguration = load_common_configuration_from_workbook(config_filename)
        self.add_middleware(
            CORSMiddleware,
            allow_origins=[common_configuration.client_url, ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.api = Application(config_filename).api_implementation


app = FastAPI2()


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get("/case_model")
async def get_case_model() -> CaseModel:
    print("********************************** get_case_model **********************************")
    # return api.get_case_model()
    return app.api.get_case_model()


@app.post("/analyze")
async def analyze(field_values: str, text: str):
    print("********************************** analyze **********************************")
    field_values2 = json.loads(field_values)
    return app.api.analyze(field_values2, text)


@app.post("/process_request")
async def handle_case(request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
    print("********************************** request **********************************")
    return app.api.handle_case(request)





API_ROUTE = "/api/v1"

@app.post(f"{API_ROUTE}/analyze", tags=["Services"])
async def analyze_v1(data: dict) -> dict[str, Any]:
    # Extract the field values from the POST request body
    field_values: dict[str, Any]= data.get("field_values", "{}")

    # Extract the message from the POST request body
    text: str = data.get("text", "")

    print("********************************** analyser_demande **********************************")
    return app.api.analyze(field_values, text)

@app.post(f"{API_ROUTE}/process_request", tags=["Services"])
async def handle_case_v1(data: dict):
    # Extract the case request object from the POST request body
    case_request= data.get("case_request", "{}")
    if isinstance(case_request, dict):
        case_request = CaseHandlingRequest(**case_request)

    print ("********************************** handle_case_v1 **********************************")
    return app.api.handle_case(case_request)

