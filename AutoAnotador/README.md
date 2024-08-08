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
