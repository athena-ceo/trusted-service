import sys

import uvicorn

from src.backend.backend.rest.main import app
from src.common.connection_configuration import ConnectionConfiguration

print(sys.argv)
if len(sys.argv) < 3:
    print("You must provide a yaml configuration file and one or more application definition files as command-line arguments, for instance:")
    print(f"python {sys.argv[0]} runtime/config_connection.yaml apps/delphes/design_time/appdef_delphes_ff.xlsx apps/conneXion/design_time/appdef_conneXion_ff.xlsx")
    exit()

config_connection_filename = sys.argv[1]
connection_configuration = ConnectionConfiguration.load_from_yaml_file(config_connection_filename)

appdef_filenames: list[str] = sys.argv[2:]

app.init(connection_configuration, appdef_filenames)

uvicorn.run(app, host=connection_configuration.rest_api_host, port=connection_configuration.rest_api_port)
