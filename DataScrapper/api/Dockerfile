FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        bash \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver

COPY DataScrapper/api/requirements.txt /tmp/api-requirements.txt
COPY DataScrapper/google-images-download/requirements.txt /tmp/scrapper-requirements.txt
COPY Limpeza/requirements.txt /tmp/limpeza-requirements.txt

RUN python -m venv /app/env_scrapper \
    && /app/env_scrapper/bin/pip install --upgrade pip \
    && /app/env_scrapper/bin/pip install -r /tmp/scrapper-requirements.txt \
    && python -m venv /app/env_limpeza \
    && /app/env_limpeza/bin/pip install --upgrade pip \
    && /app/env_limpeza/bin/pip install -r /tmp/limpeza-requirements.txt \
    && pip install --upgrade pip \
    && pip install -r /tmp/api-requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "DataScrapper.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
