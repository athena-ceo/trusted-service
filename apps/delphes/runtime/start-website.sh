#!/bin/bash

# Define the port number
PORT=5006

# Navigate to the website directory
cd website || exit

# Start a simple HTTP server on localhost
python3.12 -m http.server "$PORT" --bind 127.0.0.1 || {
  echo -e "\033[31mError: Port $PORT is already in use.\033[0m"
  exit 1
}
