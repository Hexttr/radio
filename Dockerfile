# Pirate Radio AI - Dockerfile
# Optimized for ARM64 (Oracle Cloud Free Tier)

FROM python:3.11-slim

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/music /app/output /app/cache

# Expose port (default 9090, override with STREAM_PORT env)
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9090/status || exit 1

# Run the radio
CMD ["python", "-m", "src.radio"]
