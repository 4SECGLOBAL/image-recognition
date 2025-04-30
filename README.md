# image-recognition
Este repositório contém diversas ferramentas relativas ao pipeline de Coleta e Limpeza de dados para Datasets, Treinamento e Avaliação de Modelos de Detecção de Objetos em Imagens baseados em YOLO.

## 🔧 Estrutura do Projeto

### DataScrapper
- Coletar imagens da Web baseando-se em strings de busca.
- Algoritmos para gerar strings de busca que combinem mais de uma classe, com a possibilidade de adição de contexto.

### Limpeza 
- Limpeza de imagens duplicadas e com tamanhos fora de especificações.
- Limpeza simples por hash ou limpeza com elementos visuais usando pHash.

### AutoAnotador
- Realizar a auto-anotação de imagens, podendo-se definir o modelo utilizado pelos pesos, anotar uma classe específica e desenhar as bounding boxes para análise visual.

### Avaliador
- Implementação de um avaliador de "Assertividade" -- em imagens que contém ao menos uma instância de uma classe, verifica se há ao menos uma instância daquela classe predita.

## ⚙️ Instalação
É recomendado realizar a instação das dependências utilizando os scripts de instalação

```bash
.\install_requirements.bat # Windows
# ou
./install_requirements.sh # Linux
```

## 🧩 Como Utilizar o Pipeline?

É possível utilizar cada uma das ferramentas por si só, acessando a documentação de cada uma em seus respectivos diretórios, mas é possível aplicar de forma mais automatizada, com a integração de alguns passos e feedbacks de métricas ao longo do Pipeline

### Coleta e Limpeza de Imagens
```bash
./coleta_e_limpeza.sh <termo_busca> <limite> [min_largura] [min_altura] [max_largura] [max_altura] [--limpeza_visual]
```
✅ Exemplo:
```bash
./coleta_e_limpeza.sh "Arma" 80 200 200 1280 720 --limpeza_visual
```
#### Argumentos

termo_busca: nome do arquivo (sem extensão) de termos na pasta ./DataScrapper/listas_termos

limite: número máximo de imagens a coletar

min_largura, min_altura: dimensões mínimas (padrão: 100x100)

max_largura, max_altura: dimensões máximas (padrão: 1920x1080)

--limpeza_visual (opcional): ativa método avançado para remoção de duplicatas com perceptual hash + embeddings visuais.

### Pré-Anotação
```bash
./env_model/bin/python AutoAnotador/annotator.py ./DataScrapper/images/ \
  --det_model <caminho pesos modelo pré-treinado> \
  --draw
```

✅ Exemplo:
```bash
./env_modelo/bin/python AutoAnotador/annotator.py ./DataScrapper/images/ \
  --det_model best.pt \
  --desired_class_id 2 \
  --draw
```
#### Argumentos

--det_model: nome ou caminho do modelo YOLO (ex: best.pt, yolov8x.pt).

--desired_class_id: anotar apenas uma classe específica (opcional).

--draw: salva imagens com as bounding boxes desenhadas (opcional, mas recomendado).

### Anotação Manual, Split e Data Augmentation
Atualmente, esses procedimentos são realizados por ferramentas externas, como o [RoboFlow](https://app.roboflow.com). É necessário importar as imagens coletadas em DataScrapper/images e as bounding boxes da auto-anotação (se preferir pré-anotado) em DataScrapper/images_auto_annotate_labels. Realize os ajustes nas anotações, redefina as classes se necessário, defina a proporção de split (treinamento, validação e teste), defina as operações de data augmentation e exporte com a formatação YOLOv8 ou YOLOv11.

### Treinamento
```bash
source env_model/bin/activate && yolo train data=<caminho do data.yaml do seu dataset> model=<caminho dos pesos .pt> epochs=<num epocas> batch=<tamanho do batch> imgsz=<dimensoes imagem> device=<dispositivo utilizado> cache=<True ou False>
```

✅ Exemplo:
```bash
source env_model/bin/activate && yolo train data=data.yaml model=dabest.pt epochs=5000 batch=16 imgsz=640 device=0,1,2 cache=True && deactivate
```

#### Argumentos
data: caminho para o arquivo data.yaml que define a estrutura do seu dataset.

model: nome ou caminho para o modelo pré-treinado (.pt) que será utilizado como base para o treinamento.

epochs: Número de épocas (passagens completas pelo dataset) para o treinamento. Aumentar o número de épocas pode melhorar a precisão, mas também aumenta o tempo de treinamento.​

batch: Tamanho do lote (batch size) utilizado durante o treinamento. Valores maiores podem acelerar o treinamento, mas exigem mais memória.​

imgsz: Tamanho das imagens de entrada (em pixels) para o modelo.

device: Especifica o dispositivo de computação a ser utilizado para o treinamento. Ex.: device=0: Utiliza a GPU de índice 0; device=0,1: Utiliza múltiplas GPUs (índices 0 e 1); device=cpu: Utiliza o processador (CPU)

cache: Determina se o dataset será armazenado em cache para acelerar o carregamento durante o treinamento.

### Treinamento
```bash
source env_model/bin/activate && yolo train data=<caminho do data.yaml do seu dataset> model=<caminho dos pesos .pt> epochs=<num epocas> batch=<tamanho do batch> imgsz=<dimensoes imagem> device=<dispositivo utilizado> cache=<True ou False>
```

✅ Exemplo:
```bash
source env_model/bin/activate && yolo train data=data.yaml model=dabest.pt epochs=5000 batch=16 imgsz=640 device=0,1,2 cache=True && deactivate
```

#### Avaliação