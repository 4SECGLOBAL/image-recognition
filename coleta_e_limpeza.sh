#!/bin/bash

images_dir="./DataScrapper/images/"

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
PYTHON_EXEC="./env_limpeza/bin/python"

# Verifica se o argumento --limpeza_visual foi passado
limpeza_visual_flag=""
for arg in "$@"; do
  if [ "$arg" == "--limpeza_visual" ]; then
    limpeza_visual_flag="--limpeza_visual"
    break
  fi
done

# 🟣 Início do processo
echo -e "\n🚀 Iniciando processo completo de coleta e limpeza de imagens..."
echo "🔍 Termo de busca: \"$termo_busca\""
echo "📸 Limite de imagens: $limite"
echo "📏 Filtros de tamanho → mín: ${min_larg}x${min_alt}, máx: ${max_larg}x${max_alt}"
[ ! -z "$limpeza_visual_flag" ] && echo "🖼️  Modo de limpeza visual ativado!"

# ▶️ Coleta das imagens
echo -e "\n📥 => COLETA DE IMAGENS"
cd DataScrapper
./execute.sh "$termo_busca" "$limite" -join
cd ..

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

echo -e "\n🏁 Processo completo finalizado.\n"
