#!/bin/bash
# Setup script to install dependencies before network access is disabled.
set -e

# Change to the directory of the script
cd "$(dirname "$0")"

pip install -r requirements.txt

# Verify Ollama is available for machine learning tasks
if ! command -v ollama >/dev/null 2>&1; then
    echo "Warning: Ollama CLI not found. Install it or mount it so GitSleuth can use it for ML tasks." >&2
else
    echo "Ollama CLI found at $(command -v ollama)"
fi
