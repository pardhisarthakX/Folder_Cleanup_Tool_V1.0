# ============================================
# Folder Cleanup Tool - Dockerfile
# Multi-stage build: deps -> runtime
# ============================================

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY config.json ./

RUN pip install --no-cache-dir --prefix=/install .


# --- Runtime stage ---
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY config.json ./
COPY .env.example ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/logs /data \
    && chown -R appuser:appuser /app /data

USER appuser

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Run Streamlit UI
CMD ["streamlit", "run", "src/folder_cleanup/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
