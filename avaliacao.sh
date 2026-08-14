#!/bin/bash

# No desenvolvimento local, usa o venv quando ele existir. Dentro do container,
# as dependências ficam no único Python global.
if [ -f env_model/bin/activate ]; then
  source env_model/bin/activate
fi

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

annotator_cmd=(python AutoAnotador/annotator.py "$test_path/images/" \
  --det_model "$model_path" \
  --output_dir "$test_path/images_auto_annotate_labels")
[ -n "$confidence" ] && annotator_cmd+=(--confidence "$confidence")
[ -n "$device" ] && annotator_cmd+=(--device "$device")
"${annotator_cmd[@]}"

# Verifica sucesso da execução
if [ $? -ne 0 ]; then
    echo -e "\n❌ Erro ao executar o script de auto-anotação.\n"
    exit 1
else
    echo "✅ Auto-anotação concluída e salva em: $test_path/images_auto_annotate_labels"
fi

echo -e "\n🔍 => VALIDAÇÃO YOLO NO CONJUNTO DE TESTE"
# Cria o comando de validação do YOLO. O caminho absoluto evita que o
# Ultralytics redirecione os resultados para runs/detect.
validation_project="$(pwd)/Avaliador/validacao"
validation_cmd=(python Avaliador/yolo_validation.py \
  --data "$data_yaml" \
  --model "$model_path" \
  --project "$validation_project")
[ -n "$confidence" ] && validation_cmd+=(--confidence "$confidence")
[ -n "$device" ] && validation_cmd+=(--device "$device")
[ "$save_json" = "True" ] || [ "$save_json" = "true" ] && validation_cmd+=(--save-json)

# Roda validação 
"${validation_cmd[@]}"

# Verifica sucesso da execução
if [ $? -ne 0 ]; then
    echo -e "\n❌ Erro ao executar a validação YOLO.\n"
    exit 1
else
    echo "✅ Validação concluída com sucesso e salva em: $validation_project"
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
