import sys

import streamlit as st

from src.backend.backend.trusted_services_server import TrustedServicesServer
from src.common.api import Api
from src.common.connection_configuration import ConnectionConfiguration
from src.common.logging import print_yellow
from src.client.api_client import ApiClient
from src.client.api_client_rest import ApiClientRest
from src.client.api_decorator import ApiDecorator
from src.client.main_testclient import populate_apps, main_testclient

def create_client(argv: list[str]) -> ApiClient:

    runtime_directory = argv[1]

    if argv[2] == "direct":

        api: Api = TrustedServicesServer(runtime_directory)

        return ApiDecorator(api)
    else:

        config_connection_filename = runtime_directory + "/" + "config_connection.yaml"

        connection_configuration: ConnectionConfiguration = ConnectionConfiguration.load_from_yaml_file(config_connection_filename)
        url = "http://{rest_api_host}:{rest_api_port}".format(rest_api_host=connection_configuration.rest_api_host, rest_api_port=connection_configuration.rest_api_port)
        return ApiClientRest(url)

# If the ApiClient does not exist yet then create it

print_yellow("values")

if "api_client" not in st.session_state:
    if len(sys.argv) != 3 or sys.argv[2] not in ["direct", "rest"]:
        st.write("Missing required inputs. Please provide as command-line arguments:")
        st.write("  • A runtime directory")
        st.write("  • A direct/rest flag to determine how the client connects to the Trusted Services server")
        st.write("For instance:")
        st.write(f"```streamlit run {sys.argv[0]} "
                        "./runtime "
                        "direct```")
        exit()

    api_client = create_client(sys.argv)
    st.session_state.api_client = api_client
    populate_apps(api_client)

main_testclient()
