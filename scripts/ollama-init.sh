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

# Pull chat model
echo "Pulling phi3:mini..."
if ! timeout 300 ollama pull phi3:mini; then
  echo "Failed to pull phi3:mini"
  exit 1
fi

# Pull embedding model
echo "Pulling nomic-embed-text..."
if ! timeout 300 ollama pull nomic-embed-text; then
  echo "Failed to pull nomic-embed-text"
  exit 1
fi

echo "All models pulled successfully."
exit 0