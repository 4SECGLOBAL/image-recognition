#!/bin/bash

# Verifica se há todos os argumentos necessários passados
if [ $# -lt 2 ]; then
  echo "Como usar: $0 filename limit"
  exit 1
fi

# Obtem os dados de filename e limit a partir dos argumentos
filename=$1
limit=$2

# Itera por cada linha no arquivo txt e realiza o scrap com cada termo de busca
while IFS= read -r search_term; do
  echo  "Baixando imagens para o termo: $search_term com limite de $limit imagens"
  ./venv/bin/python ./google-images-download/bing_scraper.py --search "$search_term" --limit $limit --download --chromedriver ./chromedriver.exe
done < "$filename"
