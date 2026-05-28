#!/bin/sh
set -e

mkdir -p \
  /app/Avaliador/images/train \
  /app/Avaliador/images/val \
  /app/Avaliador/labels/train \
  /app/Avaliador/labels/val \
  /app/Avaliador/test/images \
  /app/Avaliador/test/images_auto_annotate_labels \
  /app/Avaliador/test/labels \
  /app/Avaliador/validacao \
  /app/runs

# if [ ! -f /app/Avaliador/data.yaml ]; then
#   cat > /app/Avaliador/data.yaml <<'EOF'
# path: /app/Avaliador
# train: images/train
# val: images/val
# test: test/images
# nc: 2

# names:
#   0: dinheiro
#   1: cedula_20_reais
# EOF
# else
#   sed -i 's#^path: .*#path: /app/Avaliador#' /app/Avaliador/data.yaml
# fi

exec "$@"
