import inspect
import os
import json
import sys
import types
from datetime import datetime
from typing import Optional, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import traceback

from src.backend.backend.trusted_services_server import TrustedServicesServer
from src.common.server_api import ServerApi, CaseHandlingRequest, CaseHandlingDetailedResponse
from src.common.case_model import CaseModel
from src.common.config import SupportedLocale
from src.common.constants import API_ROUTE_V2
from src.common.logging import print_red
from src.backend.ruleflow.ruleflow_api import router as ruleflow_router


class AnalyzeRequest(BaseModel):
    field_values: dict[str, Any]
    text: str
    read_from_cache: bool
    llm_config_id: str


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

        # Ensure the runtime directory can be imported as the 'runtime' package.
        # Some app config/workbook values reference modules under the logical
        # package name 'runtime' (for example 'runtime.apps.delphes...'). When
        # running under uvicorn --reload the child process may not have the
        # same import context, so create a lightweight package module named
        # 'runtime' that points to the runtime_directory on disk.
        try:
            if 'runtime' not in sys.modules:
                runtime_pkg = types.ModuleType('runtime')
                # __path__ tells importlib where to look for subpackages/modules
                runtime_pkg.__path__ = [runtime_directory]
                sys.modules['runtime'] = runtime_pkg
        except Exception as exc:
            # Don't fail initialization just because we couldn't create the alias;
            # importlib may still find modules depending on sys.path. We log and
            # let downstream imports raise if needed (caught by outer try/except).
            print_red(f"Failed to create runtime import alias: {exc}")

        self.server_api: ServerApi = TrustedServicesServer(runtime_directory)


app: FastAPI2 = FastAPI2()


# If the launcher set an environment variable with the runtime directory, initialize the
# app at import time so Uvicorn's reload mode (which imports by string) can start with a
# properly initialized application.
try:
    runtime_dir_env = os.getenv("TRUSTED_SERVICES_RUNTIME_DIR")
    if runtime_dir_env:
        from src.common.connection_config import ConnectionConfig

        config_connection_filename = runtime_dir_env + "/" + "config_connection.yaml"
        connection_config = ConnectionConfig.load_from_yaml_file(config_connection_filename)
        # Only initialize if not already initialized
        if getattr(app, "server_api", None) is None:
            app.init(connection_config, runtime_dir_env)
except Exception as e:
    # Log the exception so it's visible when Uvicorn imports the module in reload mode.
    import traceback

    print("Failed to auto-initialize app during import (TRUSTED_SERVICES_RUNTIME_DIR may be missing or invalid):")
    traceback.print_exc()

else:
    # Informational message when module auto-initializes the app due to
    # TRUSTED_SERVICES_RUNTIME_DIR being present. Helpful when running
    # under uvicorn --reload so logs show what runtime directory is used.
    try:
        print(f"Initialized app during import using TRUSTED_SERVICES_RUNTIME_DIR={runtime_dir_env}")
    except Exception as exc:
        print_red(f"Failed to log TRUSTED_SERVICES_RUNTIME_DIR: {exc}")


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint for Docker healthcheck and monitoring"""
    return {
        "status": "healthy",
        "service": "trusted-services-backend",
        "timestamp": datetime.now().isoformat()
    }


@app.post(API_ROUTE_V2 + "/reload_apps", tags=["System"])
async def reload_apps():
    print_red("*** reload_apps ***")
    log_function_call()
    return app.server_api.reload_apps()


@app.get(API_ROUTE_V2 + "/app_ids", response_model=list[str], summary="Get the ids of all apps defined", tags=["App Management"])
async def get_app_ids() -> list[str]:
    log_function_call()
    return app.server_api.get_app_ids()


@app.get(API_ROUTE_V2 + "/apps/{app_id}/locales", response_model=list[str], tags=["App Management"])
async def get_locales(app_id: str) -> list[str]:
    log_function_call()
    return app.server_api.get_locales(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/llm_config_ids", response_model=list[str], tags=["Configuration"])
async def get_llm_config_ids(app_id: str) -> list[str]:
    log_function_call()
    return app.server_api.get_llm_config_ids(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/decision_engine_config_ids", response_model=list[str], tags=["Configuration"])
async def get_decision_engine_config_ids(app_id: str) -> list[str]:
    log_function_call()
    return app.server_api.get_decision_engine_config_ids(app_id)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{locale}/app_name", tags=["Metadata"])
async def get_app_name(app_id: str, locale: SupportedLocale) -> str:
    log_function_call()
    return app.server_api.get_app_name(app_id=app_id, locale=locale)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{locale}/app_description", tags=["Metadata"])
async def get_app_description(app_id: str, locale: SupportedLocale) -> str:
    log_function_call()
    return app.server_api.get_app_description(app_id=app_id, locale=locale)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{locale}/sample_message", tags=["Metadata"])
async def get_sample_message(app_id: str, locale: SupportedLocale) -> str:
    log_function_call()
    return app.server_api.get_sample_message(app_id=app_id, locale=locale)


@app.get(API_ROUTE_V2 + "/apps/{app_id}/{locale}/case_model", tags=["Metadata"])
async def get_case_model(app_id: str, locale: SupportedLocale) -> CaseModel:
    log_function_call()
    return app.server_api.get_case_model(app_id=app_id, locale=locale)


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{locale}/analyze", tags=["Analysis and Processing"])
async def analyze(app_id: str, locale: SupportedLocale, request: AnalyzeRequest):
    log_function_call()
    try:
        return app.server_api.analyze(app_id=app_id, locale=locale, field_values=request.field_values, text=request.text, read_from_cache=request.read_from_cache, llm_config_id=request.llm_config_id)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print_red(f"❌ Erreur dans l'endpoint /analyze: {type(e).__name__}: {str(e)}")
        print_red(f"Traceback:\n{error_traceback}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": error_traceback
            }
        )


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{locale}/save_text_analysis_cache", tags=["Analysis and Processing"])
async def save_text_analysis_cache(app_id: str, locale: SupportedLocale, text_analysis_cache: str):
    log_function_call()
    return app.server_api.save_text_analysis_cache(app_id, locale, text_analysis_cache)


@app.post(API_ROUTE_V2 + "/apps/{app_id}/{locale}/handle_case", tags=["Analysis and Processing"])
async def handle_case(app_id: str, locale: SupportedLocale, request: CaseHandlingRequest) -> CaseHandlingDetailedResponse:
    log_function_call()
    return app.server_api.handle_case(app_id=app_id, locale=locale, request=request)


# Include ruleflow editor API router
app.include_router(ruleflow_router)
