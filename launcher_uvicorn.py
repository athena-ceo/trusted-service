import sys

import uvicorn

from src.common.common_configuration import load_common_configuration_from_workbook, CommonConfiguration

from src.backend.backend.rest.main import app

if len(sys.argv) == 1:
    print("You must provide a configuration file as a command-line argument")
    print("For instance:", f"python launcher_uvicorn.py {sys.argv[0]} apps/delphes/runtime/configuration_delphes.xlsx")
    exit()

config_filename = sys.argv[1]  # Read from main.py

app.set_config_filename(config_filename)

common_configuration: CommonConfiguration = load_common_configuration_from_workbook(config_filename)

uvicorn.run(app,
            host=common_configuration.rest_api_host,
            port=common_configuration.rest_api_port)
