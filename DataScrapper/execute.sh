#!/bin/bash

# Verifica se há todos os argumentos necessários passados
if [ -z "$1" ] || [ -z "$2" ]; then
  echo -e "\n🚫 Uso incorreto!"
  echo "Uso: $0 <nome_do_arquivo> <limite> [-join]"
  exit 1
fi

# Diretórios padrão
termos_dir="./listas_termos/"
images_dir="./images/"

# Parâmetros
filename="$termos_dir$1.txt"
limit="$2"
junta="$3"
PYTHON_EXEC="../env_scrapper/bin/python"

# Contador
total_images_downloaded=0
declare -A images_per_term

echo -e "\n🚀 Iniciando download de imagens..."
echo "Arquivo de termos: $filename"
echo "Limite por termo: $limit"
echo ""

# Itera por cada termo no arquivo
while IFS= read -r search_term || [ -n "$search_term" ]; do
  echo -e "\n🔍 Termo: \"$search_term\""

  $PYTHON_EXEC ./google-images-download/bing_scraper.py --search "$search_term" --limit $limit --download --chromedriver /usr/local/bin/chromedriver -i "$filename"

  search_dir="$images_dir${search_term// /_}"
  if [ -d "$search_dir" ]; then
    images_downloaded=$(find "$search_dir" -type f | wc -l)
    images_per_term["$search_term"]=$images_downloaded
    total_images_downloaded=$((total_images_downloaded + images_downloaded))
    echo "Imagens baixadas: $images_downloaded"
  else
    echo "⚠️  Diretório não encontrado: $search_dir"
    images_per_term["$search_term"]=0
  fi
done < "$filename"

# Resumo por termo
echo -e "\n📊 Resumo:"
for term in "${!images_per_term[@]}"; do
  echo "'$term' → ${images_per_term[$term]}/$limit"
done

# Total final
echo -e "\n✅ Total de imagens baixadas com sucesso: $total_images_downloaded"
echo "Imagens salvas em: $images_dir"

# Junta imagens se solicitado
if [ "$junta" == "-join" ]; then
  echo -e "\n🔗 Unindo imagens em um único diretório..."

  while IFS= read -r line || [ -n "$line" ]; do
    current_dir="$images_dir${line// /_}"
    
    if [ ! -d "$current_dir" ]; then
      echo "⚠️  Diretório inexistente: $current_dir"
      continue
    fi

    echo "Movendo imagens de: $current_dir"
    mv "$current_dir"/* "$images_dir"
    rmdir "$current_dir" && echo "Diretório removido: $current_dir"
  done < "$filename"

  echo -e "\n📦 Todas as imagens foram reunidas no diretório: $images_dir"
fi

echo -e "\n🏁 Concluído.\n"
