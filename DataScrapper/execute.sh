#!/bin/bash

# Verifica se há todos os argumentos necessários passados
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 filename limit [-join]"
  exit 1
fi

# Obtém os dados de filename, limit e a flag de juntar a partir dos argumentos
filename="$1"
limit="$2"
junta="$3"

# Itera por cada linha no arquivo txt e realiza o scrap com cada termo de busca
while IFS= read -r search_term; do
  echo  "Baixando imagens para o termo: $search_term com limite de $limit imagens"
  ./venv/bin/python ./google-images-download/bing_scraper.py --search "$search_term" --limit $limit --download --chromedriver ./chromedriver.exe  --image-directory $filename
done < "$filename"

# Verifica se o terceiro argumento é '-join'
if [ "$junta" == "-join" ]; then
  # Diretório selecionado
  current_dir="./images/$filename"
  echo "Diretório selecionado: $current_dir"

  # Verifica se o diretório existe
  if [ ! -d "$current_dir" ]; then
    echo "Erro: O diretório $current_dir não existe."
    exit 1
  fi

  # Itera por todas as pastas dentro do diretório selecionado
  for dir in "$current_dir"/*/; do
    echo "Processando pasta: $dir"

    # Move todos os arquivos de todas as pastas para o diretório superior
    mv "$dir"* "$current_dir"

    # Deleta as pastas
    rmdir "$dir"
  done

  echo "Todos os arquivos foram movidos e as pastas foram deletadas."
else
  echo "Invalid argument: $junta"
  echo "Usage: $0 filename limit [-join]"
fi