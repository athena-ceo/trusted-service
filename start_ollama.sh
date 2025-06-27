#!/bin/bash

# Set default values from environment variables or fallback defaults
LLM_SERVICE="${DELPHES_LLM_SERVICE:-OpenAI}"  # Default to 'OpenAI' if not set
LLM_MODEL="${DELPHES_LLM_MODEL:-gpt-4o-mini}"  # Default to 'gpt-4o-mini' if not set
LOCAL_MODE=""

# Parse input arguments
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --llm-service)
      LLM_SERVICE="$2"
      shift 2
      ;;
    --llm-model)
      LLM_MODEL="$2"
      shift 2
      ;;
    --local)
      LOCAL_MODE="--local"
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      exit 1
      ;;
  esac
done

# Function to check if Ollama is running with the correct model
function check_ollama_status {
  # Check if Ollama is running
  if ! pgrep -x "ollama" > /dev/null; then
    echo "Ollama is not running. Starting Ollama daemon..."
    nohup ollama run $LLM_MODEL > /dev/null 2>&1 &
    sleep 3  # Give it time to initialize
  else
    # Check if the correct model is installed locally
    if ! ollama list | awk '{print $1}' | grep -Fxq "$LLM_MODEL"; then
        echo "Model $LLM_MODEL not found locally. Pulling..."
        ollama pull "$LLM_MODEL"
    fi

    # Verify if Ollama is running the correct model
    RUNNING_MODEL=$(ollama ps | awk '{print $1}' | grep -Fx "$LLM_MODEL")
    if [[ -z "$RUNNING_MODEL" ]]; then
        echo "Ollama is running, but not with model $LLM_MODEL. Restarting..."
        # Stop Ollama safely by specifying the model name
        CURRENT_MODEL=$(ollama ps | awk 'NR>1 {print $1}')  # Get the first running model
        if [[ -n "$CURRENT_MODEL" ]]; then
            echo "Stopping current model: $CURRENT_MODEL"
            ollama stop "$CURRENT_MODEL"
            sleep 2
        fi
        echo "Starting model: $LLM_MODEL"
        ollama run "$LLM_MODEL" > /dev/null 2>&1 &
        sleep 3
    else
        echo "Ollama is already running with model $LLM_MODEL."
    fi
  fi
}

# Start Ollama if required
if [[ "$LLM_SERVICE" == "Ollama" ]]; then
  check_ollama_status
fi
