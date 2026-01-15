# Use the official Ollama image as the base
FROM ollama/ollama

# The base image is minimal and doesn't include curl.
# We install it so our init script can perform health checks.
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*