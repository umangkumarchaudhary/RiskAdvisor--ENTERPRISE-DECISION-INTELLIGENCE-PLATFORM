# RiskAdvisor v4.0 - Docker Build
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip install --no-cache-dir python-dotenv psycopg2-binary

# Application code
COPY . .

# Expose port
EXPOSE 8000

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run with proper production settings
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
