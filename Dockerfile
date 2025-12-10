FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (if we have one, otherwise we'll install in the container)
# For now, we'll install dependencies directly

# Copy the application code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    flask \
    flask-cors \
    requests \
    canvasapi \
    python-docx \
    beautifulsoup4 \
    toml

# Expose the port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run the API server
CMD ["python3", "update-canvas-api.py"]

