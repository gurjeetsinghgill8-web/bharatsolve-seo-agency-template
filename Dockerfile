# BHARATSOLVE SEO AGENCY — Docker
# Single-command deploy: docker-compose up
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for PDF outputs
RUN mkdir -p pdf_outputs

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501', timeout=5)" || exit 1

# Run the app
CMD ["streamlit", "run", "app.py", "--server.headless=true", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]
