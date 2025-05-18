FROM python:3.11-slim-bookworm

# Встановлення бібліотек
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Копіювання файлів
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Створення /tmp (на всяк випадок)
RUN mkdir -p /tmp

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && ls -R staticfiles && gunicorn shop.wsgi:application --log-level debug --log-file -"]
