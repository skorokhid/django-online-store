FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --prefer-binary \
    --timeout=300 \
    -r requirements.txt

COPY . .