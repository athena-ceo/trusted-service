import json
from typing import Optional

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
