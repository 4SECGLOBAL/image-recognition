# AutoAnotador

Implementação para anotar automaticamente imagens usando um modelo de detecção em imagens YOLO. A função *auto_annotator* processa todas as imagens em um determinado diretório e detecta objetos usando o modelo YOLO. A anotação resultante é salva como um aquivo de texto para cada imagem, no formato [xi yi width height] normalizado. Adaptado de [Ultralytics YOLO](https://docs.ultralytics.com/reference/data/annotator/#ultralytics.data.annotator.auto_annotate).

## Requirements

Para utilizar esse software, você deve utilizar Python 3.8 ou superior. Utiliza-se ambientes virtuais de Python para evitar conflito de dependencias no sistema. Instalar *virtualenv* com:

```bash
pip install virtualenv
```

Dependencias podem ser instaladas da seguinte maneira:

### Windows
```bash
python -m virtualenv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
### Linux
```bash
python3 -m virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Como utilizar

### Como executável Python
1) Acessar a linha de comando
2) Executar o script com os parâmetros desejados:
```
# Com parâmetros padrão
python annotator.py <caminho pra pasta de imagens>
# Com parâmetros customizados
python annotator.py <caminho pra pasta de imagens> --det_model <caminho do modelo> --device <id do dispositivo> --output_dir <caminho do diretorio de saida> --desired_class_id <id da classe desejada para anotacao> --draw <True ou False>
```

### Como biblioteca
1) Acessar um ambiente python (digitando `python` ou `python3` no terminal) ou dentro de algum outro script
2) Importar a função *auto_annotate*:
```
 >>> from AutoAnotador.annotator import auto_annotate
```
3) Executar a função com os parâmetros desejados:
```
 >>> auto_annotate(data='data_dir/', det_model='best.pt', device='cuda', output_dir = 'output_dir/')
```

## Parâmetros
- data (str): Caminho para a pasta com as imagens a ser anotadas.

- det_model (str): Caminho ou nome do modelo YOLO pre-treinado.

- device (str): Dispositivo que vai processar o modelo (e.g., 'cpu', 'cuda', '0').

- output_dir (str | None): Diretorio para salvar os resultados anotados. Se for None, um diretorio padrao sera criado.

- desired_class_id (int | None): Id específico caso queira anotar somente uma classe.

- draw (bool | False): Desenha as bounding boxes nas imagens respectivas e salva no output_dir.
