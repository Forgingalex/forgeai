FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860

WORKDIR /app

# system dependencies + supervisor (CRITICAL)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl supervisor \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# the application code
COPY . .

# Hugging Face requires port 7860
EXPOSE 7860

# Run supervisor to launch both FastAPI and the Celery Worker
CMD ["supervisord", "-c", "supervisord.conf"]