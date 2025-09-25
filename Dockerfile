FROM python:3.10-slim

WORKDIR /app

# Dependências
RUN apt-get update && apt-get install -y ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

# Whisper + FastAPI
RUN pip install --no-cache-dir faster-whisper fastapi uvicorn

COPY app /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
