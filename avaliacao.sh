#!/bin/bash

PYTHON_ENV=env_model/bin/activate

# Activate the virtual environment
source $PYTHON_ENV

# Parse arguments from the shell script
data_yaml=$1
model_path=$2
test_path=$3
confidence=${4:-}  # Optional confidence
device=${5:-}      # Optional device
save_json=${6:-}   # Optional save_json

# Início do processo
echo -e "\n🚀 Iniciando processo completo de avaliação..."
echo "📄 YAML do dataset: $data_yaml"
echo "📸 Modelo: $model_path"
echo "📏 Imagens de validação: $test_path"
[ ! -z "$confidence" ] && echo "🔍 Confiança: $confidence"
[ ! -z "$device" ] && echo "💻 Dispositivo: $device"
[ ! -z "$save_json" ] && echo "💾 JSON: $save_json"

echo -e "\n✍️ => AUTO-ANOTAÇÃO"

# python AutoAnotador/annotator.py $test_path/images/ \
#   --det_model $model_path \
#   --draw

# Verifica sucesso da execução
if [ $? -ne 0 ]; then
    echo -e "\n❌ Erro ao executar o script de auto-anotação.\n"
    exit 1
else
    echo "✅ Auto-anotação concluída e salva em: $test_path/images_auto_annotate_labels"
fi

echo -e "\n🔍 => VALIDAÇÃO YOLO NO CONJUNTO DE TESTE"
# Cria o comando de validação do YOLO
yolo_cmd="yolo detect val data=$data_yaml model=$model_path plots=True project=Avaliador/validacao"
[ -n "$confidence" ] && yolo_cmd+=" conf=$confidence"
[ -n "$device" ] && yolo_cmd+=" device=$device"
[ -n "$save_json" ] && yolo_cmd+=" save_json=$save_json"

# Roda validação 
eval $yolo_cmd

# Verifica sucesso da execução
if [ $? -ne 0 ]; then
    echo -e "\n❌ Erro ao executar a validação YOLO.\n"
    exit 1
else
    echo "✅ Validação concluída com sucesso e salva em : $test_path../runs/detect/val"
fi

echo -e "\n🔍 => VALIDAÇÃO DE ASSERTIVIDADE NO CONJUNTO DE TESTE"
# Roda o script de assertividade
python Avaliador/image_assertivity.py $test_path/labels/ $test_path/images_auto_annotate_labels --yaml_path $data_yaml --check_fp True --save True

# Verifica sucesso da execução
if [ $? -ne 0 ]; then
    echo -e "\n❌ Erro ao executar a validação de assertividade.\n"
    exit 1
else
    echo "✅ Validação de assertividade concluída com sucesso"
fi

echo -e "\n🏁 Avaliação completa finalizada.\n"