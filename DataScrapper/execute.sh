#!/bin/bash

# Verifica se há todos os argumentos necessários passados
if [ -z "$1" ] || [ -z "$2" ]; then
  echo -e "\n🚫 Uso incorreto!"
  echo "Uso: $0 <nome_do_arquivo> <limite> [-join]"
  exit 1
fi

# Diretórios padrão
termos_dir="./listas_termos/"
images_dir="${DATASCRAPPER_IMAGES_DIR:-./images/}"
images_dir="${images_dir%/}/"

mkdir -p "$images_dir"
chmod 777 "$images_dir" 2>/dev/null || true

images_parent="$(dirname "$images_dir")"
images_basename="$(basename "$images_dir")"
if [ "$(basename "$images_parent")" = "images" ]; then
  labels_dir="$(dirname "$images_parent")/images_auto_annotate_labels/$images_basename"
  mkdir -p "$labels_dir"
  chmod 777 "$labels_dir" 2>/dev/null || true
fi

# Parâmetros
filename="$termos_dir$1.txt"
limit="$2"
junta="$3"
PYTHON_EXEC="../env_scrapper/bin/python"

# Contador
total_images_downloaded=0
declare -A images_per_term

count_images_in_dir() {
  find "$images_dir" -maxdepth 1 -type f | wc -l
}

sanitize_prefix() {
  echo "$1" | tr ' /' '__'
}

echo -e "\n🚀 Iniciando download de imagens..."
echo "Arquivo de termos: $filename"
echo "Limite por termo: $limit"
echo ""

# Itera por cada termo no arquivo
while IFS= read -r search_term || [ -n "$search_term" ]; do
  [ -z "$search_term" ] && continue
  echo -e "\n🔍 Termo: \"$search_term\""
  images_before=$(count_images_in_dir)
  prefix="$(sanitize_prefix "$search_term")"

  echo "🌐 Motor: Bing"
  $PYTHON_EXEC ./google-images-download/bing_scraper.py --search "$search_term" --limit $limit --download --chromedriver /usr/local/bin/chromedriver -o "$images_dir" --flat_directory --prefix "bing_$prefix"
  bing_status=$?

  echo "🌐 Motor: Google"
  $PYTHON_EXEC ./google-images-download/google_scraper.py --search "$search_term" --limit "$limit" --download --chromedriver /usr/local/bin/chromedriver -o "$images_dir" --flat_directory --prefix "google_$prefix"
  google_status=$?

  if [ $bing_status -eq 0 ] || [ $google_status -eq 0 ]; then
    images_after=$(count_images_in_dir)
    images_downloaded=$((images_after - images_before))
    images_per_term["$search_term"]=$images_downloaded
    total_images_downloaded=$((total_images_downloaded + images_downloaded))
    echo "Imagens baixadas: $images_downloaded"
  else
    echo "⚠️  Falha ao baixar imagens para o termo em todos os motores: $search_term"
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
  echo -e "\n📦 As imagens já foram salvas diretamente no diretório: $images_dir"
fi

echo -e "\n🏁 Concluído.\n"
