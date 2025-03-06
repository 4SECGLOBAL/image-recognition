# Criado por Gustavo Fardo Armenio. 
# Adaptado de Ultralytics YOLO (https://docs.ultralytics.com/reference/data/annotator/#ultralytics.data.annotator.auto_annotate)

from pathlib import Path

from ultralytics import YOLO

import cv2

def auto_annotate(data, det_model="yolov8x.pt", device="", output_dir=None, desired_class_id=None, draw=False):
    """
    Anota automaticamente imagens usando um modelo de detecção em imagens YOLO.

    Essa função processa todas as imagens em um determinado diretório e detecta objetos usando o modelo YOLO. A anotação resultante é salva como um aquivo de texto para cada imagem, no formato [xi yi width height] normalizado.
    
    Args:
        data (str): Caminho para a pasta com as imagens a ser anotadas.
        det_model (str): Caminho ou nome do modelo YOLO pre-treinado.
        device (str): Dispositivo que vai processar o modelo (e.g., 'cpu', 'cuda', '0').
        output_dir (str | None): Diretorio para salvar os resultados anotados. Se for None, um diretorio padrao sera criado.
        desired_class_id (int | None): ID da classe desejada para anotar. Se for None, todas as classes serao anotadas.
        draw (bool): Se True, desenha as bounding boxes na imagem original e salva a imagem anotada.

    Exemplos:
        >>> from AutoAnotador.annotator import auto_annotate
        >>> auto_annotate(data='data_dir/', det_model='best.pt')

    Notas:
        - A funcao cria um novo diretorio para saida caso nao for especificado.
        - Resultados de anotacao sao salvos como arquivos de texto com o mesmo nome do arquivo de imagem.
        - Cada linha no arquivo de texto de saida representa um objeto detectado com o ID da sua classe e os pontos da bounding box, no formato [xi yi width height] normalizado com o tamanho da imagem.
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
        if draw == True:
            img = cv2.imread(result.path)

        if len(class_ids):
            boxes = result.boxes.xywhn  # Bounding Boxes de uma imagem em formato xywh normalizado

            filtered_boxes = []
            filtered_class_ids = []

            # Filtra as bounding boxes pela class_id desejada se desired_class_id não for None
            for i in range(len(class_ids)):
                if desired_class_id is None or class_ids[i] == desired_class_id:
                    filtered_boxes.append(boxes[i])
                    filtered_class_ids.append(class_ids[i])

                    if draw == True:
                        box = boxes[i]
                        x_center, y_center, width, height = box
                        x_center *= img.shape[1]
                        y_center *= img.shape[0]
                        width *= img.shape[1]
                        height *= img.shape[0]

                        x1 = int(x_center - width / 2)
                        y1 = int(y_center - height / 2)
                        x2 = int(x_center + width / 2)
                        y2 = int(y_center + height / 2)

                        # Desenha a bounding box
                        img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        # Desenha o ID da classe
                        img = cv2.putText(img, str(class_ids[i]), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if len(filtered_boxes) > 0:
                with open(f"{Path(output_dir) / Path(result.path).stem}.txt", "w") as f:
                    # Escreve cada bounding box filtrada em uma nova linha do arquivo de texto
                    for i in range(len(filtered_boxes)):
                        b = filtered_boxes[i]
                        if len(b) == 0:
                            continue
                        box = map(str, filtered_boxes[i].reshape(-1).tolist())
                        f.write(f"{filtered_class_ids[i]} " + " ".join(box) + "\n")
                    if draw == True:
                        output_image_path = Path(output_dir) / f"{Path(result.path).stem}_annotated.jpg"
                        print("Salvando imagem anotada no diretorio " + str(output_image_path)) 
                        cv2.imwrite(str(output_image_path), img)