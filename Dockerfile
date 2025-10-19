FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Переменная окружения для порта
ENV PORT=8080

# Открываем порт 8080 (необязательно для Cloud Run, но полезно для тестов локально)
EXPOSE 8080

# Запускаем приложение
CMD ["gunicorn", "-w", "1", "-k", "gevent", "-b", "0.0.0.0:8080", "--timeout", "60", "main:app"]
