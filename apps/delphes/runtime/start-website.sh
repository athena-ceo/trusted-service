#!/bin/bash

# Define the port number
PORT=8080

# Navigate to the website directory
cd website || exit

# Start a simple HTTP server on localhost
python -m http.server "$PORT" --bind 127.0.0.1 || {
  echo -e "\033[31mError: Port $PORT is already in use.\033[0m"
  exit 1
}
