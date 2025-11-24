# Use a small Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system deps (if you use postgres, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement list first (for better caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Environment for Flask app factory
ENV FLASK_APP="nira:create_app"
ENV FLASK_ENV="production"

# Gunicorn will serve your app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "nira:create_app()"]
