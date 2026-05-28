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

COPY AutoAnotador/api/requirements.txt /tmp/api-requirements.txt
COPY AutoAnotador/requirements.txt /tmp/annotator-requirements.txt

RUN python -m venv /app/env_model \
    && /app/env_model/bin/pip install --upgrade pip \
    && /app/env_model/bin/pip install -r /tmp/annotator-requirements.txt \
    && pip install --upgrade pip \
    && pip install -r /tmp/api-requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "AutoAnotador.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
