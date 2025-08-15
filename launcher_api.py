import sys

import uvicorn

from src.backend.backend.rest.main import app
from src.backend.backend.server_configuration import ServerConfiguration
from src.common.connection_configuration import ConnectionConfiguration

if len(sys.argv) < 4:
    print("Missing required inputs. Please provide as command-line arguments:")
    print("  • A YAML file containing the connection configuration for the Trusted Services server.")
    print("  • A YAML file containing the execution configuration for the Trusted Services server.")
    print("  • One or more xlsx application definition files.")
    print("For instance:")
    print(f"python {sys.argv[0]} "
          "runtime/config_connection.yaml "
          "runtime/config_server.yaml "
          "apps/delphes/design_time/appdef_delphes_ff.xlsx "
          "apps/conneXion/design_time/appdef_conneXion_ff.xlsx")
else:

    config_connection_filename = sys.argv[1]
    connection_configuration = ConnectionConfiguration.load_from_yaml_file(config_connection_filename)

    config_server_filename = sys.argv[2]
    server_configuration = ServerConfiguration.load_from_yaml_file(config_server_filename)

    appdef_filenames: list[str] = sys.argv[3:]

    app.init(connection_configuration, appdef_filenames)

    uvicorn.run(app, host=connection_configuration.rest_api_host,
                port=connection_configuration.rest_api_port,
                access_log=True)
