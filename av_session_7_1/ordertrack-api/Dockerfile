FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Entrypoint waits for the DB, seeds it, then starts Flask (see docker-compose).
CMD ["python", "app.py"]
