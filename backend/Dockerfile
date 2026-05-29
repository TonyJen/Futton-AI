FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/backend/data

COPY backend /app/backend
COPY data /app/data

EXPOSE 8000

CMD ["sh", "-c", "if [ ! -f /app/backend/data/futon_manufacturing.db ]; then FUTON_DB_FILE=/app/backend/data/futon_manufacturing.db python /app/data/seed.py; fi && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
