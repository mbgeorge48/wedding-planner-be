# Use a slim Python image for a smaller footprint
FROM python:3.13-slim AS builder

# Install curl and ca-certificates to download Tailwind safely
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download standalone Tailwind CLI (pinned version for stability)
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.1/tailwindcss-linux-x64 \
    && chmod +x tailwindcss-linux-x64 \
    && mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss

WORKDIR /app
COPY . .

# Verify tailwindcss binary and files before building
RUN tailwindcss --help > /dev/null
RUN ls -l ./project/interfaces/web/static/style.css

# Build minified CSS to a temporary file then move it (safer than in-place)
RUN tailwindcss -i ./project/interfaces/web/static/style.css -o ./project/interfaces/web/static/style-built.css --minify \
    && mv ./project/interfaces/web/static/style-built.css ./project/interfaces/web/static/style.css

# Final production image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .
# Copy the built CSS from the builder stage
COPY --from=builder /app/project/interfaces/web/static/style.css ./project/interfaces/web/static/style.css

# Ensure the entrypoint script is executable
RUN chmod +x scripts/entrypoint

# Set the entrypoint
ENTRYPOINT ["/app/scripts/entrypoint"]
