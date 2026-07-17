# Inferencia

Executa predicao YOLO em uma imagem e salva uma copia com as bounding boxes desenhadas.

## Execucao Manual

Use a partir da raiz do projeto:

```bash
env_model/bin/python Inferencia/inferir.py
```

Por padrao, o script usa:

- modelo: `runs/detect/train-11/weights/best.pt`
- imagem: `Inferencia/foto3.jpg`
- resultado: `Inferencia/resultado.jpg`

## Informando Parametros

```bash
env_model/bin/python Inferencia/inferir.py \
  --model runs/detect/train-11/weights/best.pt \
  --image Inferencia/foto3.jpg \
  --output Inferencia/resultado.jpg \
  --conf 0.05
```

Parametros:

- `--model`: caminho do arquivo `.pt` treinado.
- `--image`: caminho da imagem de entrada.
- `--output`: caminho onde a imagem com deteccoes sera salva.
- `--conf`: confianca minima entre `0.0` e `1.0`. Exemplo: `0.05` equivale a 5%.

O terminal mostra a classe e a confianca de cada deteccao:

```text
Deteccao 1: cedula_20_reais - confianca 99.99%
Resultado salvo em: Inferencia/resultado.jpg
```

## Dependencias

Se o ambiente ainda nao tiver o Ultralytics instalado:

```bash
env_model/bin/pip install ultralytics
```

Para usar a API FastAPI da inferencia:

```bash
env_model/bin/pip install -r Inferencia/api/requirements.txt
```

## API Via Docker Compose

Suba o servico:

```bash
docker compose up --build inference-api
```

A documentacao interativa fica em:

```text
http://localhost:8004/docs
```

Endpoint:

```text
POST http://localhost:8004/api/4/inferencia/
```

Exemplo de payload:

```json
{
  "model": "runs/detect/train-11/weights/best.pt",
  "image": "Inferencia/foto3.jpg",
  "confianca": 0.05,
  "data_yaml": "Avaliador/data.yaml",
  "label": "Avaliador/test/labels/foto3.txt",
  "iou_threshold": 0.5
}
```

A resposta inclui `resultado_url`, apontando para a imagem salva em `Inferencia/resultado.jpg`.
Quando a API encontra o arquivo `.txt` YOLO ground truth correspondente a imagem, tambem gera
`Inferencia/matriz_confusao.jpg` e retorna os dados em `matriz_confusao`.

O campo `label` e opcional. Se ele nao for enviado, a API procura um `.txt` com o mesmo nome da
imagem em:

- mesma pasta da imagem
- `Avaliador/labels/train`
- `Avaliador/labels/val`
- `Avaliador/test/labels`
- `Inferencia/labels`

Se nenhum label ground truth for encontrado, a inferencia continua normalmente e
`matriz_confusao.status` retorna `label_ground_truth_nao_encontrado`.
