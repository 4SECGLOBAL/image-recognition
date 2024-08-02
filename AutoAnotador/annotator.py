# Criado por Gustavo Fardo Armenio. 
# Adaptado de Ultralytics YOLO (https://docs.ultralytics.com/reference/data/annotator/#ultralytics.data.annotator.auto_annotate)

from pathlib import Path

from ultralytics import YOLO

def auto_annotate(data, det_model="yolov8x.pt", device="", output_dir=None):
    """
    Anota automaticamente imagens usando um modelo de detecção em imagens YOLO.

    Essa função processa todas as imagens em um determinado diretório e detecta objetos usando o modelo YOLO. A anotação resultante é salva como um aquivo de texto para cada imagem, no formato [xi yi xf yf] normalizado.
    
    Args:
        data (str): Caminho para a pasta com as imagens a ser anotadas.
        det_model (str): Caminho ou nome do modelo YOLO pre-treinado.
        device (str): Dispositivo que vai processar o modelo (e.g., 'cpu', 'cuda', '0').
        output_dir (str | None): Diretorio para salvar os resultados anotados. Se for None, um diretorio padrao sera criado.

    Exemplos:
        >>> from AutoAnotador.annotator import auto_annotate
        >>> auto_annotate(data='data_dir/', det_model='best.pt')

    Notas:
        - A funcao cria um novo diretorio para saida caso nao for especificado.
        - Resultados de anotacao sao salvos como arquivos de texto com o mesmo nome do arquivo de imagem.
        - Cada linha no arquivo de texto de saida representa um objeto detectado com o ID da sua classe e os pontos da bounding box, no formato [xi yi xf yf] normalizado com o tamanho da imagem.
    """
    det_model = YOLO(det_model)

    # Le os dados do diretorio de entrada e cria diretorio de saida se nao existir
    data = Path(data)
    if not output_dir:
        output_dir = data.parent / f"{data.stem}_auto_annotate_labels"
    Path(output_dir).mkdir(exist_ok=True, parents=True)

    # Faz a inferencia em todas as imagens
    det_results = det_model(data, stream=True, device=device)

    # Escreve as bounding boxes das imagens em arquivos de texto
    for result in det_results:
        class_ids = result.boxes.cls.int().tolist()  # noqa
        if len(class_ids):
            boxes = result.boxes.xyxyn  # Bounding Boxes de uma imagem em formato xyxy normalizado

            with open(f"{Path(output_dir) / Path(result.path).stem}.txt", "w") as f:
                # Escreve cada bounding box em uma nova linha do arquivo de texto
                for i in range(len(boxes)):
                    b = boxes[i]
                    if len(b) == 0:
                        continue
                    box = map(str, boxes[i].reshape(-1).tolist())
                    f.write(f"{class_ids[i]} " + " ".join(box) + "\n")