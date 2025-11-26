FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# force compatible Flask + Werkzeug
RUN pip install --no-cache-dir "Flask==2.0.3" "Werkzeug==2.0.3"

COPY . .

ENV FLASK_APP="nira:create_app"
ENV FLASK_ENV="production"

CMD ["gunicorn", "-b", "0.0.0.0:8000", "nira:create_app()"]
