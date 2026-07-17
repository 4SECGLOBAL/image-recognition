from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import yaml


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".avif"}


@dataclass
class YoloBox:
    class_id: int
    xyxy: tuple[float, float, float, float]


@dataclass
class ConfusionMatrixResult:
    output_file: Path
    label_file: Path
    classes: list[str]
    matrix: list[list[int]]
    iou_threshold: float
    matched: int
    false_positives: int
    false_negatives: int


def load_class_names(data_yaml: Path) -> list[str]:
    with data_yaml.open("r", encoding="utf-8") as data_file:
        data = yaml.safe_load(data_file) or {}

    names = data.get("names") or {}
    if isinstance(names, list):
        return [str(name) for name in names]
    if isinstance(names, dict):
        return [str(name) for _, name in sorted(((int(key), value) for key, value in names.items()))]

    raise ValueError("Campo names invalido ou ausente em data.yaml.")


def find_label_file(image_file: Path, explicit_label: Path | None, repo_root: Path) -> Path | None:
    if explicit_label is not None:
        return explicit_label if explicit_label.exists() else None

    adjacent_label = image_file.with_suffix(".txt")
    if adjacent_label.exists():
        return adjacent_label

    candidates = [
        repo_root / "Avaliador" / "labels" / "train" / adjacent_label.name,
        repo_root / "Avaliador" / "labels" / "val" / adjacent_label.name,
        repo_root / "Avaliador" / "test" / "labels" / adjacent_label.name,
        repo_root / "Inferencia" / "labels" / adjacent_label.name,
    ]
    return next((candidate for candidate in candidates if candidate.exists()), None)


def read_yolo_labels(label_file: Path, image_width: int, image_height: int) -> list[YoloBox]:
    boxes: list[YoloBox] = []
    with label_file.open("r", encoding="utf-8") as labels:
        for raw_line in labels:
            parts = raw_line.strip().split()
            if len(parts) < 5:
                continue

            class_id = int(float(parts[0]))
            x_center, y_center, width, height = (float(value) for value in parts[1:5])
            x1 = (x_center - width / 2) * image_width
            y1 = (y_center - height / 2) * image_height
            x2 = (x_center + width / 2) * image_width
            y2 = (y_center + height / 2) * image_height
            boxes.append((YoloBox(class_id=class_id, xyxy=(x1, y1, x2, y2))))

    return boxes


def calculate_iou(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> float:
    x1 = max(first[0], second[0])
    y1 = max(first[1], second[1])
    x2 = min(first[2], second[2])
    y2 = min(first[3], second[3])

    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    first_area = max(0.0, first[2] - first[0]) * max(0.0, first[3] - first[1])
    second_area = max(0.0, second[2] - second[0]) * max(0.0, second[3] - second[1])
    union = first_area + second_area - intersection
    return intersection / union if union else 0.0


def build_confusion_matrix(
    ground_truth: list[YoloBox],
    predictions: list[YoloBox],
    class_count: int,
    iou_threshold: float,
) -> tuple[np.ndarray, int, int, int]:
    background_index = class_count
    matrix = np.zeros((class_count + 1, class_count + 1), dtype=np.int32)

    possible_matches = []
    for gt_index, gt_box in enumerate(ground_truth):
        for pred_index, pred_box in enumerate(predictions):
            iou = calculate_iou(gt_box.xyxy, pred_box.xyxy)
            if iou >= iou_threshold:
                possible_matches.append((iou, gt_index, pred_index))

    matched_gt: set[int] = set()
    matched_pred: set[int] = set()
    for _, gt_index, pred_index in sorted(possible_matches, reverse=True):
        if gt_index in matched_gt or pred_index in matched_pred:
            continue

        gt_box = ground_truth[gt_index]
        pred_box = predictions[pred_index]
        if gt_box.class_id < class_count and pred_box.class_id < class_count:
            matrix[gt_box.class_id, pred_box.class_id] += 1
        matched_gt.add(gt_index)
        matched_pred.add(pred_index)

    for gt_index, gt_box in enumerate(ground_truth):
        if gt_index not in matched_gt and gt_box.class_id < class_count:
            matrix[gt_box.class_id, background_index] += 1

    for pred_index, pred_box in enumerate(predictions):
        if pred_index not in matched_pred and pred_box.class_id < class_count:
            matrix[background_index, pred_box.class_id] += 1

    return matrix, len(matched_gt), len(predictions) - len(matched_pred), len(ground_truth) - len(matched_gt)


def draw_confusion_matrix(matrix: np.ndarray, labels: list[str], output_file: Path) -> None:
    cell_size = 96
    left_margin = 220
    top_margin = 150
    right_margin = 40
    bottom_margin = 80
    size = len(labels)
    width = left_margin + size * cell_size + right_margin
    height = top_margin + size * cell_size + bottom_margin
    canvas = np.full((height, width, 3), 255, dtype=np.uint8)
    max_value = int(matrix.max()) or 1

    cv2.putText(canvas, "Matriz de Confusao", (left_margin, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (20, 20, 20), 2)
    cv2.putText(canvas, "Predito", (left_margin + size * cell_size // 2 - 45, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (60, 60, 60), 2)
    cv2.putText(canvas, "Real", (35, top_margin + size * cell_size // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (60, 60, 60), 2)

    for index, label in enumerate(labels):
        short_label = label[:22]
        x = left_margin + index * cell_size + 8
        y = top_margin - 20
        cv2.putText(canvas, short_label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (30, 30, 30), 1)
        row_y = top_margin + index * cell_size + cell_size // 2 + 5
        cv2.putText(canvas, short_label, (left_margin - 205, row_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 1)

    for row in range(size):
        for col in range(size):
            value = int(matrix[row, col])
            intensity = int(235 - (190 * value / max_value))
            color = (255, intensity, intensity)
            x1 = left_margin + col * cell_size
            y1 = top_margin + row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, -1)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), (220, 220, 220), 1)
            text = str(value)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)[0]
            text_x = x1 + (cell_size - text_size[0]) // 2
            text_y = y1 + (cell_size + text_size[1]) // 2
            cv2.putText(canvas, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_file), canvas)


def generate_confusion_matrix(
    *,
    data_yaml: Path,
    image_file: Path,
    explicit_label: Path | None,
    predictions: list[YoloBox],
    output_file: Path,
    repo_root: Path,
    iou_threshold: float,
) -> ConfusionMatrixResult | None:
    class_names = load_class_names(data_yaml)
    label_file = find_label_file(image_file, explicit_label, repo_root)
    if label_file is None:
        return None

    image = cv2.imread(str(image_file))
    if image is None:
        raise ValueError(f"Nao foi possivel ler a imagem: {image_file}")

    image_height, image_width = image.shape[:2]
    ground_truth = read_yolo_labels(label_file, image_width, image_height)
    matrix, matched, false_positives, false_negatives = build_confusion_matrix(
        ground_truth=ground_truth,
        predictions=predictions,
        class_count=len(class_names),
        iou_threshold=iou_threshold,
    )
    labels = [*class_names, "background"]
    draw_confusion_matrix(matrix, labels, output_file)

    return ConfusionMatrixResult(
        output_file=output_file,
        label_file=label_file,
        classes=labels,
        matrix=matrix.tolist(),
        iou_threshold=iou_threshold,
        matched=matched,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )
