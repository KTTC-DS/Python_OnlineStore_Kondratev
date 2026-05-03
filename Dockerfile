# Используем официальный образ Python
FROM python:3.12-slim

# Отключаем буферизацию вывода, чтобы логи были видны сразу
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем postgresql-client (для pg_isready)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . /app/

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Открываем порт 8000
EXPOSE 8000

# Запускаем сервер разработки
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]