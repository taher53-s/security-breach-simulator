FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY setup.py README.md ./
COPY src/ ./src/
COPY backend/ ./backend/
COPY tests/ ./tests/
COPY docs/ ./docs/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose API port
EXPOSE 8000

# Default command runs API server
CMD ["uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
