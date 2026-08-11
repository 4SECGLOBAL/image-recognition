#!/bin/bash

images_dir="${DATASCRAPPER_IMAGES_DIR:-./DataScrapper/images/}"
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

# Variáveis obrigatórias
termo_busca=$1
limite=$2
min_larg=$3
min_alt=$4
max_larg=$5
max_alt=$6

# Define valores padrão, se não forem fornecidos
min_larg=${min_larg:-100}
min_alt=${min_alt:-100}
max_larg=${max_larg:-1920}
max_alt=${max_alt:-1080}

# Caminho para o interpretador Python
if [ -x ./env_limpeza/bin/python ]; then
  PYTHON_EXEC="./env_limpeza/bin/python"
else
  PYTHON_EXEC="python"
fi

# Verifica flags opcionais
limpeza_flag="true"
limpeza_visual_flag=""
anonimo_flag=""
for arg in "$@"; do
  if [ "$arg" == "--sem_limpeza" ]; then
    limpeza_flag="false"
  fi
  if [ "$arg" == "--limpeza_visual" ]; then
    limpeza_visual_flag="--limpeza_visual"
  fi
  if [ "$arg" == "--anonimo" ]; then
    anonimo_flag="--anonimo"
  fi
done

# 🟣 Início do processo
echo -e "\n🚀 Iniciando processo completo de coleta e limpeza de imagens..."
echo "🔍 Termo de busca: \"$termo_busca\""
echo "📸 Limite de imagens: $limite"
echo "📏 Filtros de tamanho → mín: ${min_larg}x${min_alt}, máx: ${max_larg}x${max_alt}"
[ "$limpeza_flag" == "false" ] && echo "🧹 Limpeza do dataset desativada."
[ ! -z "$limpeza_visual_flag" ] && echo "🖼️  Modo de limpeza visual ativado!"
[ ! -z "$anonimo_flag" ] && echo "🕶️  Modo anonimo ativado para o ChromeDriver!"

# ▶️ Coleta das imagens
echo -e "\n📥 => COLETA DE IMAGENS"
cd DataScrapper
./execute.sh "$termo_busca" "$limite" -join $anonimo_flag
cd ..

if [ "$limpeza_flag" == "false" ]; then
    echo -e "\n⏭️  Limpeza do dataset pulada."
    echo "🧾 Imagens finais salvas em: $images_dir"
else
    # ▶️ Limpeza do dataset
    echo -e "\n🧹 => LIMPEZA DO DATASET"

    $PYTHON_EXEC Limpeza/limpeza_dataset.py "$images_dir" \
      --min_width "$min_larg" \
      --min_height "$min_alt" \
      --max_width "$max_larg" \
      --max_height "$max_alt" \
      $limpeza_visual_flag

    # Verifica sucesso da execução
    if [ $? -ne 0 ]; then
        echo -e "\n❌ Erro ao executar o script de limpeza.\n"
        exit 1
    else
        echo "🧾 Imagens finais salvas em: $images_dir"
    fi
fi

echo -e "\n🏁 Processo completo finalizado.\n"
