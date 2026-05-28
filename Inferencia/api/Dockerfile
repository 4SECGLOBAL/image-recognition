FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    YOLO_CONFIG_DIR=/tmp/Ultralytics

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY Inferencia/api/requirements.txt /tmp/api-requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /tmp/api-requirements.txt

COPY . /app

RUN mkdir -p /app/Inferencia /app/runs

EXPOSE 8000

CMD ["uvicorn", "Inferencia.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
