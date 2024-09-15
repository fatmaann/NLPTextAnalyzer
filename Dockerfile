# Используем официальный Python-образ версии 3.10
FROM python:3.10-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y build-essential

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт (например, для Streamlit)
EXPOSE 8501

# Запускаем приложение
CMD ["streamlit", "run", "app.py"]
