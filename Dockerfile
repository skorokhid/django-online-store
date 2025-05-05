FROM python:3.11-slim-bookworm 

RUN apt-get update && apt-get install -y \
    libgl1 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --prefer-binary \
    --timeout=300 \
    -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]