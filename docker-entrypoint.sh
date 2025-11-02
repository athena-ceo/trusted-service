#!/bin/bash
set -e

# Docker entrypoint script for backend
# Ensures config is set up correctly for containerized environment

RUNTIME_DIR="${1:-./runtime}"
CONFIG_FILE="$RUNTIME_DIR/config_connection.yaml"

echo "🐳 Starting Trusted Services Backend in Docker"
echo "📁 Runtime directory: $RUNTIME_DIR"

# Create runtime directories if they don't exist
mkdir -p "$RUNTIME_DIR/cache"

# Check if config exists, if not create a default one
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚙️  Creating default config_connection.yaml"
    cat > "$CONFIG_FILE" <<EOF
client_url: "http://localhost:8501"
rest_api_host: "0.0.0.0"
rest_api_port: 8002
EOF
else
    # Config exists, but we need to ensure it uses 0.0.0.0 for Docker
    echo "⚙️  Updating config to bind to 0.0.0.0 for Docker"
    # Use sed to replace 127.0.0.1 with 0.0.0.0 in place
    sed -i 's/rest_api_host: "127.0.0.1"/rest_api_host: "0.0.0.0"/' "$CONFIG_FILE" || true
    sed -i "s/rest_api_host: '127.0.0.1'/rest_api_host: '0.0.0.0'/" "$CONFIG_FILE" || true
fi

echo "✅ Configuration ready"
echo "🚀 Launching backend..."

# Execute the Python application with all arguments
exec python launcher_api.py "$@"

