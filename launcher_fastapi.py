import json
import sys
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.backend.backend.api_implementation import ApiImplementation
from src.backend.backend.application import Application
from src.backend.decision.decision import CaseHandlingDecisionInput, CaseHandlingDecisionOutput
from src.common.api import Api, CaseHandlingRequest, CaseHandlingResponse, CaseHandlingDetailedResponse
from src.common.case_model import CaseModel

if len(sys.argv) == 1:
    print("You must provide a configuration file as a command-line argument")
    print("For instance:", f"streamlit run {sys.argv[0]} apps/delphes/runtime/configuration_delphes.xlsx")
    exit()

app = FastAPI()

origins = [
    "http://localhost:8501/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application = Application("apps/delphes/runtime/configuration_delphes.xlsx")
api: Api = application.api_implementation


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get("/case_model")
async def get_case_model() -> CaseModel:
    print("********************************** get_case_model **********************************")
    return api.get_case_model()


@app.post("/analyze")
async def analyze(field_values: str, text: str):
    print("********************************** analyze **********************************")
    field_values2 = json.loads(field_values)
    return api.analyze(field_values2, text)


@app.post("/process_request")
async def handle_case(request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
    print("********************************** request **********************************")
    return api.handle_case(request)
