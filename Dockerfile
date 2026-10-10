# OmniPress MCP Server — Multi-arch Container (Node.js + Python + ffmpeg)
FROM node:20-bookworm-slim

# Install system dependencies: ffmpeg for video rendering, Python 3 for neural TTS
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create Python virtual environment and install edge-tts for dark channel voice generation
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir edge-tts requests pydantic

# Copy application source
COPY . .

# Create persistent storage directories
RUN mkdir -p /app/articles /app/media/staging /app/media/output /app/media/assets

ENV PORT=3333
ENV OMNIPRESS_MODE=http
ENV ARTICLES_DIR=/app/articles
ENV MEDIA_STAGING_DIR=/app/media/staging

EXPOSE 3333

# Run OmniPress HTTP & OpenAPI Gateway by default
CMD ["node", "src/server.js", "--http", "3333"]
