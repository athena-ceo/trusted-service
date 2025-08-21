import sys

import uvicorn

from src.backend.backend.rest.main import app
from src.common.connection_config import ConnectionConfig

if len(sys.argv) != 2:
    print("Missing required inputs. Please provide as command-line arguments:")
    print("  • A runtime directory")
    print("For instance:")
    print(f"python {sys.argv[0]} "
          "./runtime")
else:
    runtime_directory = sys.argv[1]

    config_connection_filename = runtime_directory + "/" + "config_connection.yaml"
    connection_config = ConnectionConfig.load_from_yaml_file(config_connection_filename)

    app.init(connection_config, runtime_directory)

    uvicorn.run(app, host=connection_config.rest_api_host,
                port=connection_config.rest_api_port,
                access_log=True)
