FROM python:3.11-slim-bookworm

# Оновлення та встановлення залежностей
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Встановлення робочої директорії
WORKDIR /app

# Оновлення pip
RUN pip install --upgrade pip

# Копіювання та установка залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --prefer-binary \
    --timeout=300 \
    -r requirements.txt

# Копіювання коду
COPY . .

# Команда для запуску (буде перевизначена в Render Docker Command)
CMD ["gunicorn", "shop.wsgi:application"]  # Замініть "shop" на назву вашого проєкту