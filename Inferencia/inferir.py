import argparse
from pathlib import Path

from ultralytics import YOLO


def inferir(model_path: str, image_path: str, output_path: str, conf: float | None = None) -> None:
    model_file = Path(model_path)
    image_file = Path(image_path)
    output_file = Path(output_path)

    if not model_file.exists():
        raise FileNotFoundError(f"Modelo nao encontrado: {model_file}")
    if not image_file.exists():
        raise FileNotFoundError(f"Imagem nao encontrada: {image_file}")

    model = YOLO(str(model_file))
    kwargs = {"conf": conf} if conf is not None else {}
    results = model(str(image_file), **kwargs)
    result = results[0]

    if result.boxes is None or len(result.boxes) == 0:
        print("Nenhuma deteccao encontrada.")
    else:
        for i, box in enumerate(result.boxes, start=1):
            class_id = int(box.cls.item())
            class_name = result.names[class_id]
            confidence = float(box.conf.item())
            print(f"Deteccao {i}: {class_name} - confianca {confidence:.2%}")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    result.save(filename=str(output_file))
    print(f"Resultado salvo em: {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa inferencia YOLO em uma imagem.")
    parser.add_argument("--model", default="runs/detect/train-21/weights/best.pt", help="Caminho do modelo .pt treinado.")
    parser.add_argument("--image", default="Inferencia/crime1.jpg", help="Caminho da imagem de entrada.")
    parser.add_argument("--output", default="Inferencia/resultado.jpg", help="Caminho da imagem de saida.")
    parser.add_argument("--conf", type=float, default=None, help="Confianca minima opcional, ex: 0.05.")
    args = parser.parse_args()

    inferir(args.model, args.image, args.output, args.conf)


if __name__ == "__main__":
    main()
