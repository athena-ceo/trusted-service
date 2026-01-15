import argparse
import os
import uvicorn
from dotenv import load_dotenv

from src.backend.backend.rest.main import app
from src.common.connection_config import ConnectionConfig


def main() -> None:
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Launch the Trusted Services API using a runtime directory."
    )
    parser.add_argument(
        "runtime_directory",
        help="Path to the runtime directory (contains config_connection.yaml)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Start uvicorn with auto-reload (useful for development).",
    )
    parser.add_argument(
        "--lenient",
        action="store_true",
        help="Validation mode: if set, server starts even if some apps have validation errors (warnings logged). "
             "Default (strict mode): server stops if any app validation fails.",
    )

    args = parser.parse_args()

    runtime_directory = os.path.abspath(args.runtime_directory)

    config_connection_filename = runtime_directory + "/" + "config_connection.yaml"
    connection_config = ConnectionConfig.load_from_yaml_file(config_connection_filename)
    
    # Determine validation mode
    validation_mode = "lenient" if args.lenient else "strict"
    os.environ["APP_VALIDATION_MODE"] = validation_mode

    # When using reload, uvicorn must import the application from an import string.
    # In that mode we pass the runtime directory via an environment variable so the
    # imported module can initialize itself on import-time (see src.backend.backend.rest.main).
    if args.reload:
        os.environ.setdefault("TRUSTED_SERVICES_RUNTIME_DIR", runtime_directory)
        import_string = "src.backend.backend.rest.main:app"
        print(f"Starting uvicorn in reload mode using import {import_string} (runtime={runtime_directory})")
        uvicorn.run(
            import_string,
            host=connection_config.rest_api_host,
            port=connection_config.rest_api_port,
            access_log=True,
            reload=True,
        )
    else:
        # Normal mode: initialize app here and pass the app object to uvicorn
        print(f"Starting uvicorn with app object (runtime={runtime_directory})")
        app.init(connection_config, runtime_directory)
        uvicorn.run(
            app,
            host=connection_config.rest_api_host,
            port=connection_config.rest_api_port,
            access_log=True,
            reload=False,
        )


if __name__ == "__main__":
    main()
