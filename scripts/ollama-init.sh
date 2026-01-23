#!/bin/bash
# This script waits for the Ollama server to be ready and then pulls the required model.

set -e

echo "Waiting for Ollama to be ready..."
RETRY_COUNT=0
while ! curl -s -o /dev/null http://localhost:11434; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -gt 30 ]; then
    echo "Ollama failed to start after 30 seconds"
    exit 1
  fi
  sleep 1
done
echo "Ollama is ready. Pulling required models..."

# Pull models to pull
MODELS=("phi3:mini" "nomic-embed-text" "llama3.2:3b" "thewindmom/llama3-med42-8b")

for MODEL in "${MODELS[@]}"; do
    echo "Processing model: $MODEL..."
    # Check if model already exists to save time/bandwidth
    if ollama list | grep -q "$MODEL"; then
        echo "$MODEL already exists, skipping pull."
    else
        echo "Pulling $MODEL..."
        if ! timeout 600 ollama pull "$MODEL"; then
            echo "Failed to pull $MODEL"
            exit 1
        fi
    fi
done

echo "All models pulled successfully."
exit 0