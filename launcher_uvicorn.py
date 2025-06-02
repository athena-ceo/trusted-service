import sys

import uvicorn

if len(sys.argv) == 1:
    print("You must provide a configuration file as a command-line argument")
    print("For instance:", f"python launcher_uvicorn.py {sys.argv[0]} apps/delphes/runtime/configuration_delphes.xlsx")
    # exit()

# config_filename = sys.argv[1]

config_filename = "apps/delphes/runtime/configuration_delphes_ff.xlsx"

uvicorn.run("main:app", port=8003)
