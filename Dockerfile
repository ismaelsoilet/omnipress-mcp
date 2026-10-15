# OmniPress MCP Server — Multi-arch Container (Node.js + Python + ffmpeg + uv)
FROM node:20-bookworm-slim

# Install system dependencies: ffmpeg for video rendering, Python 3, curl, truetype fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official astral-sh binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY package.json package-lock.json ./
RUN npm ci

COPY pyproject.toml uv.lock ./

# Install Python dependencies using frozen lockfile
ENV UV_SYSTEM_PYTHON=1
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY . .
RUN uv sync --frozen --no-dev

# Create persistent storage directories
RUN mkdir -p /app/articles /app/media/staging /app/media/output /app/media/assets /app/channels

ENV PORT=3333
ENV OMNIPRESS_MODE=http
ENV ARTICLES_DIR=/app/articles
ENV MEDIA_STAGING_DIR=/app/media/staging

EXPOSE 3333

# Run OmniPress MCP Server in HTTP/SSE mode by default
CMD ["uv", "run", "python", "src/server.py", "--http", "3333"]

