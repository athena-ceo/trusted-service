import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.backend.application import Application
from src.common.api import Api, CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.case_model import CaseModel

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

application = Application("apps/delphes/runtime/configuration_delphes_ff.xlsx")
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
