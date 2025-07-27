# Используем Python 3.11 вместо 3.13
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем все файлы проекта внутрь контейнера
COPY . .

# Обновим pip и установим зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Команда запуска
CMD ["python", "main.py"]
