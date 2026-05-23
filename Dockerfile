# Use a slim Python image for a smaller footprint
FROM python:3.13-slim as builder

# Install curl to download Tailwind
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Download standalone Tailwind CLI
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 \
    && chmod +x tailwindcss-linux-x64 \
    && mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss

WORKDIR /app
COPY . .

# Build minified CSS
RUN tailwindcss -i ./project/interfaces/web/static/style.css -o ./project/interfaces/web/static/style.css --minify

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

# Copy project code and the built CSS from the builder stage
COPY . .
COPY --from=builder /app/project/interfaces/web/static/style.css ./project/interfaces/web/static/style.css

# Ensure the entrypoint script is executable
RUN chmod +x scripts/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
