FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

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

RUN pip install --upgrade pip \
    && pip install \
        -r /tmp/scrapper-requirements.txt \
        -r /tmp/limpeza-requirements.txt \
        -r /tmp/api-requirements.txt

COPY DataScrapper /app/DataScrapper
COPY Limpeza /app/Limpeza
COPY coleta_e_limpeza.sh /app/coleta_e_limpeza.sh

RUN chmod +x /app/coleta_e_limpeza.sh /app/DataScrapper/execute.sh \
    && mkdir -p \
        /app/DataScrapper/images \
        /app/DataScrapper/images_auto_annotate_labels

EXPOSE 8000

CMD ["uvicorn", "DataScrapper.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
