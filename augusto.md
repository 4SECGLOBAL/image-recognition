# Pipeline

## Requisitos

```sh
git submodule update --init --recursive

python3 -m venv env_scrapper
 ./env_scrapper/bin/pip install -r DataScrapper/google-images-download/requirements.txt

python3 -m venv env_limpeza
./env_limpeza/bin/pip install -r Limpeza/requirements.txt
```

Container Docker reconhecer a GPU:
```sh
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```


## 1. Coleta/Scrapper

Definir os termos.

./coleta_e_limpeza.sh "Dinheiro" 80 200 200 1280 720 --limpeza_visual

Verificar a pasta `DataScrapper/imagens`.


## 2. Anotação YOLO

Label images descriptions. As imagens e os respectivos labels devem ter o mesmo nome base. Nunca separe uma imagem do seu label.

### 2.1. Manual

As primeiras anotações em formato YOLO sugiro ser realizado pela tool `yolo-labelling-tool` PreAnotacao, disponível aqui no projeto. `http://localhost:3000/`. 
Salvar as imagens+labels em `DataScrapper/images_auto_annotate_labels/<date>`.

### 2.2. AutoAnotador

python AutoAnotador/annotator.py ./DataScrapper/images/   --det_model yolov8n.pt 

Verificar a pasta `images_auto_annotable_lagels`.

### 3.2. Correção anotação

```sh
# Troca qualquer classe para 0
find . -type f -name "*.txt" -exec sed -i 's/^[0123456789]\([[:space:]]\)/0\1/' {} +
```


## 3. Treinamento

### 3.1. Montando o DataSet
O arquivo Avaliador/data.yaml define o dataset. Ver `/Avaliador/api/entrypoint.sh`. 
```sh
path: /app/Avaliador
train: images/train
val: images/val
test: test/images
nc: 2
names:
  0: dinheiro
  1: cedula_20_reais
```

Corrigir manualmente as anotações (txt) para classes YOLOs que não correspondem à classe aqui treinada.

Distribuição das imagens+anotações (endpoint distribute faz isso):
```sh
Avaliador/images/train     <- 70% das imagens
Avaliador/labels/train     <- labels dessas imagens

Avaliador/images/val       <- 20% das imagens
Avaliador/labels/val       <- labels dessas imagens

Avaliador/test/images      <- 10% das imagens
Avaliador/test/labels      <- labels dessas imagens
```

Hierarquia de pastas + `data.yaml` = Dataset:
```sh
Avaliador/
├── images
│   ├── train
│   └── val
├── labels
│   ├── train
│   └── val
├── test
│   ├── images
│   ├── images_auto_annotate_labels
│   └── labels
└── validacao
```

### 3.2. Treino
No meu caso, só tenho uma GPU
```sh
 yolo train data=Avaliador/data.yaml model=yolov8n.pt epochs=1 batch=4 imgsz=640 device=0 cache=False
 ```
Gera novo modelo: best.pt, em runs/train.

Parâmetros do comando:

- `yolo train`: executa o modo de treinamento do Ultralytics YOLO.
- `data=Avaliador/data.yaml`: informa o arquivo YAML que descreve o dataset, com os caminhos de treino, validação, teste e nomes das classes.
- `model=yolov8n.pt`: define o modelo base usado para iniciar o treinamento. Neste caso, `yolov8n.pt` é o YOLOv8 nano pré-treinado.
- `epochs=1`: número de épocas de treinamento. Uma época significa passar uma vez por todo o conjunto de treino. Para teste rápido, `1` é suficiente; para treinamento real, usar mais épocas.
- `batch=4`: quantidade de imagens processadas por vez. Valores maiores podem acelerar o treino, mas usam mais memória da GPU.
- `imgsz=640`: tamanho para redimensionamento das imagens durante o treino. O padrão comum do YOLO é `640`.
- `device=0`: usa a GPU de índice `0`. Para CPU, usar `device=cpu`.
- `cache=False`: não carrega o dataset inteiro em cache. Ajuda a evitar uso excessivo de memória.


## 4. Avaliação

mkdir -p Avaliador/test/images Avaliador/test/labels

cp Avaliador/images/val/* Avaliador/test/images/
cp Avaliador/labels/val/* Avaliador/test/labels/


python AutoAnotador/annotator.py Avaliador/test/images/ \
  --det_model runs/detect/train-5/weights/best.pt


./avaliacao.sh Avaliador/data.yaml runs/detect/train-5/weights/best.pt Avaliador/test/ "" 0


## 5. Inferencia: Testar Detecção de Objeto usando o modelo

python inferencia/inferir.py 
