import streamlit

from src.sample_frontend.streamlit_main import streamlit_direct_main
import sys

# Print all command line arguments
print(sys.argv)

if len(sys.argv) == 1:
    streamlit.write("You must provide one or more application definition files as command-line arguments, for instance:")
    streamlit.write(f"```streamlit run {sys.argv[0]} apps/delphes/design_time/appdef_delphes_ff.xlsx apps/conneXion/design_time/appdef_conneXion_ff.xlsx```")
else:
    streamlit_direct_main(sys.argv[1:])
