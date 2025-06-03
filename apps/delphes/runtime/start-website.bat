@echo off

:: Define the port number
set PORT=8080

:: Navigate to the website directory
cd website || exit /b

:: Start a simple HTTP server on localhost
python -m http.server %PORT% || (
  echo Error: Port %PORT% is already in use.
  exit /b 1
)