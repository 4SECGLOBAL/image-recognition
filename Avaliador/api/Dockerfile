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

COPY Avaliador/api/requirements.txt /tmp/api-requirements.txt
COPY AutoAnotador/requirements.txt /tmp/model-requirements.txt

RUN python -m venv /app/env_model \
    && /app/env_model/bin/pip install --upgrade pip \
    && /app/env_model/bin/pip install -r /tmp/model-requirements.txt \
    && pip install --upgrade pip \
    && pip install -r /tmp/api-requirements.txt

COPY . /app

RUN chmod +x /app/Avaliador/api/entrypoint.sh

RUN mkdir -p \
        /app/Avaliador/images/train \
        /app/Avaliador/images/val \
        /app/Avaliador/labels/train \
        /app/Avaliador/labels/val \
        /app/Avaliador/test/images \
        /app/Avaliador/test/images_auto_annotate_labels \
        /app/Avaliador/test/labels \
        /app/Avaliador/validacao \
        /app/runs \
    && if [ ! -f /app/Avaliador/data.yaml ]; then \
        printf "path: /app/Avaliador\ntrain: images/train\nval: images/val\ntest: test/images\nnc: 2\n\nnames:\n  0: dinheiro\n  1: cedula_20_reais\n" > /app/Avaliador/data.yaml; \
    fi

EXPOSE 8000

ENTRYPOINT ["sh", "/app/Avaliador/api/entrypoint.sh"]
CMD ["uvicorn", "Avaliador.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
