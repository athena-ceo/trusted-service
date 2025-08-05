import streamlit

from src.sample_frontend.streamlit_main import streamlit_rest_main
import sys

# Print all command line arguments
print(sys.argv)

if len(sys.argv) != 2:
    streamlit.write("You must provide a yaml configuration file as command-line argument, for instance:")
    streamlit.write(f"```streamlit run {sys.argv[0]} runtime/config_connection.yaml```")
else:
    streamlit_rest_main(sys.argv[1])
