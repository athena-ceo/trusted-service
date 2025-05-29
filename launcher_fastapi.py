from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.backend.api_implementation import ApiImplementation
from src.common.api import Api, CaseHandlingRequest, CaseHandlingResponse
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

api: Api = ApiImplementation()


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get("/case_model")
async def get_case_model() -> CaseModel:
    print("2) get_case_model", api.get_case_model())
    return api.get_case_model()


@app.post("/analyze")
async def analyze(field_values: dict[str, Any], text: str):
    return api.analyze(field_values, text)


@app.post("/analyze_and_render")
async def analyze_and_render(field_values: dict[str, Any], text: str):
    return api.analyze_and_render(field_values, text)

@app.post("/process_request")
async def process_request(request: CaseHandlingRequest) -> CaseHandlingResponse:
    print("3) process_request", request)
    return api.handle_case(request)