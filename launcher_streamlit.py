from src.sample_frontend.streamlit_main import streamlit_main
import sys

# Print all command line arguments
print(sys.argv)

if len(sys.argv) == 1:
    print("You must provide a configuration file as a command-line argument")
    print("For instance:", f"streamlit run {sys.argv[0]} apps/delphes/runtime/configuration_delphes.xlsx")
    exit()
else:
    streamlit_main(sys.argv[1])
