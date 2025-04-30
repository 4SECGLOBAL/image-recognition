# Criado por Gustavo Fardo Armenio. 
# Adaptado de Ultralytics YOLO (https://docs.ultralytics.com/reference/data/annotator/#ultralytics.data.annotator.auto_annotate)

from pathlib import Path
from collections import Counter
from ultralytics import YOLO
import cv2
import argparse
import numpy as np

def auto_annotate(data, det_model="yolov8x.pt", device="", output_dir=None, desired_class_id=None, draw=False):
    """
    Anota automaticamente imagens usando um modelo de detecção em imagens YOLO.

    Essa função processa todas as imagens em um determinado diretório e detecta objetos usando o modelo YOLO. A anotação resultante é salva como um aquivo de texto para cada imagem, no formato [xi yi width height] normalizado.
    
    Args:
        data (str): Caminho para a pasta com as imagens a ser anotadas.
        det_model (str | "yolov8x.pt"): Caminho ou nome do modelo YOLO pre-treinado.
        device (str | ""): Dispositivo que vai processar o modelo (e.g., 'cpu', 'cuda', '0').
        output_dir (str | None): Diretorio para salvar os resultados anotados. Se for None, um diretorio padrao sera criado.
        desired_class_id (int | None): ID da classe desejada para anotar. Se for None, todas as classes serao anotadas.
        draw (bool | False): Se True, desenha as bounding boxes na imagem original e salva a imagem anotada.

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
    if data.suffix == ".txt":
        with open(data, "r") as file:
            image_paths = [line.strip() for line in file.readlines()]
        data = image_paths
    Path(output_dir).mkdir(exist_ok=True, parents=True)

    print("🔍 Iniciando Inferência YOLO para detecção de objetos nas imagens...")

    # Faz a inferencia em todas as imagens
    det_results = det_model(data, device=device)

    # Exibe resultados detalhados por imagem
    print("\n🖼️  Resultados por Imagem\n")

    print(f"Imagem       |       Detecção")
    print(f"------------------------------")
    for result in det_results:
        class_ids = result.boxes.cls.int().tolist()  # noqa
        # Exibe o nome do arquivo e o resumo da detecção para cada imagem processada
        class_counts = Counter([det_model.names[c] for c in class_ids])
        summary = ', '.join(f"{v} {k}" for k, v in class_counts.items())
        print(f"{Path(result.path).name} | {summary}")

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

                        np.random.seed(class_ids[i])  # garante que a cor seja sempre a mesma para o mesmo ID
                        color = tuple(int(x) for x in np.random.randint(0, 255, size=3))

                        # Desenha a bounding box com a cor da classe
                        img = cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

                        # Desenha o nome da classe com a mesma cor
                        img = cv2.putText(img, str(det_model.names[class_ids[i]]), (x1, y1 + 20),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 4)
                        
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
                        cv2.imwrite(str(output_image_path), img)

    print(f"\n💾 Salvando imagens anotadas no diretório: {str(output_dir)}") 
    print("\n✅ Anotação automática concluída com sucesso!")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Auto annotate images using a YOLO model.")
    parser.add_argument("data", type=str, help="Caminho para a pasta contendo as imagens para anotar.")
    parser.add_argument("--det_model", type=str, default="yolov8x.pt", help="Caminho ou nome do modelo YOLO.")
    parser.add_argument("--device", type=str, default="", help="Dispositivo para rodar o modelo (e.g., 'cpu', 'cuda', '0').")
    parser.add_argument("--output_dir", type=str, default=None, help="Diretório para salvar os resultados anotados.")
    parser.add_argument("--desired_class_id", type=int, default=None, help="ID da classe para anotar. Anota todas as classes se não especificado.")
    parser.add_argument("--draw", action="store_true", help="Desenha as bounding boxes nas imagens originais e as salva.")

    args = parser.parse_args()

    auto_annotate(
        data=args.data,
        det_model=args.det_model,
        device=args.device,
        output_dir=args.output_dir,
        desired_class_id=args.desired_class_id,
        draw=args.draw,
    )
