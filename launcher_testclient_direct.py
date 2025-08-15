import streamlit

from src.backend.backend.server_configuration import ServerConfiguration
from src.sample_frontend.streamlit_main import streamlit_direct_main
import sys

if len(sys.argv) < 3:
    streamlit.write("Missing required inputs. Please provide as command-line arguments:")
    streamlit.write("  • A YAML file containing the execution configuration for the Trusted Services server.")
    streamlit.write("  • One or more xlsx application definition files.")
    streamlit.write("For instance:")
    streamlit.write(f"```streamlit run {sys.argv[0]} "
                    "runtime/config_server.yaml "
                    "apps/delphes/design_time/appdef_delphes_ff.xlsx "
                    "apps/conneXion/design_time/appdef_conneXion_ff.xlsx```")

else:
    config_server_filename = sys.argv[1]
    server_configuration = ServerConfiguration.load_from_yaml_file(config_server_filename)

    appdef_filenames: list[str] = sys.argv[2:]

    streamlit_direct_main(server_configuration, appdef_filenames)
