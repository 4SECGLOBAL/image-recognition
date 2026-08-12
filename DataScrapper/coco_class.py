"""Baixa e valida o COCO 2017 no formato esperado pelo Ultralytics YOLO.

Este arquivo apenas prepara o dataset. O treinamento deve ser executado em uma
etapa separada, depois que as classes e os labels do projeto forem unificados
com as 80 classes COCO.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import random
import shutil
import time
import zipfile

import requests
import yaml

try:
    from tqdm import tqdm as TQDM
except ImportError:
    def TQDM(iterable, **_: object):
        return iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_DIR = PROJECT_ROOT / "DataScrapper" / "datasets" / "coco"
DEFAULT_LIMITED_DIR = PROJECT_ROOT / "DataScrapper" / "datasets" / "coco20k"
MIN_FREE_BYTES = 45 * 1024**3
COCO_ANNOTATIONS_URL = (
    "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"
)


def log(message: str) -> None:
    """Exibe o andamento imediatamente, inclusive em logs sem buffer."""
    print(f"[COCO] {message}", flush=True)


def download_and_extract(url: str, destination: Path) -> None:
    """Baixa um ZIP sem exigir o pacote completo do Ultralytics."""
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / Path(url).name
    if not archive.exists() or archive.stat().st_size == 0:
        log(f"Baixando anotações de {url} ...")
        temporary = archive.with_suffix(archive.suffix + ".part")
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with temporary.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output.write(chunk)
        temporary.replace(archive)
        log(f"Download das anotações concluído: {archive}")
    else:
        log(f"Arquivo de anotações já existe; reutilizando: {archive}")
    log(f"Extraindo anotações em {destination} ...")
    with zipfile.ZipFile(archive) as zipped:
        zipped.extractall(destination)
    log("Extração das anotações concluída.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa as imagens train/val e os labels de detecção do COCO 2017."
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=DEFAULT_DATASET_DIR,
        help=f"Diretório final do COCO (padrão: {DEFAULT_DATASET_DIR}).",
    )
    parser.add_argument(
        "--include-test",
        action="store_true",
        help="Baixa também test2017 (sem anotações públicas; ~41 mil imagens).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Baixa somente esta quantidade de imagens (90%% treino, 10%% validação).",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed da seleção limitada.")
    parser.add_argument(
        "--workers", type=int, default=8, help="Downloads simultâneos no modo limitado."
    )
    return parser.parse_args()


def count_files(directory: Path, pattern: str) -> int:
    return sum(1 for _ in directory.glob(pattern)) if directory.exists() else 0


def download_coco(dataset_dir: Path, include_test: bool = False) -> None:
    from ultralytics.utils import ASSETS_URL
    from ultralytics.utils.downloads import download

    dataset_dir = dataset_dir.expanduser().resolve()
    dataset_dir.parent.mkdir(parents=True, exist_ok=True)
    log(f"Iniciando preparação do COCO 2017 completo em {dataset_dir}")

    free_bytes = shutil.disk_usage(dataset_dir.parent).free
    log(f"Espaço livre disponível: {free_bytes / 1024**3:.1f} GiB")
    if free_bytes < MIN_FREE_BYTES:
        raise RuntimeError(
            f"Espaço insuficiente em {dataset_dir.parent}: "
            f"{free_bytes / 1024**3:.1f} GiB livres. Reserve ao menos 45 GiB "
            "para os ZIPs temporários e o COCO train/val extraído, ou informe "
            "outro disco com --dataset-dir."
        )

    (dataset_dir / "images").mkdir(parents=True, exist_ok=True)
    log("Baixando e extraindo os labels YOLO do COCO 2017 ...")
    download([f"{ASSETS_URL}/coco2017labels.zip"], dir=dataset_dir.parent, threads=1)
    log("Labels preparados.")

    image_urls = [
        "http://images.cocodataset.org/zips/train2017.zip",
        "http://images.cocodataset.org/zips/val2017.zip",
    ]
    if include_test:
        image_urls.append("http://images.cocodataset.org/zips/test2017.zip")
    splits = "train2017, val2017" + (" e test2017" if include_test else "")
    log(f"Baixando e extraindo imagens de {splits} ...")
    download(image_urls, dir=dataset_dir / "images", threads=len(image_urls))
    log("Download das imagens concluído. Contando arquivos ...")

    train_images = count_files(dataset_dir / "images" / "train2017", "*.jpg")
    val_images = count_files(dataset_dir / "images" / "val2017", "*.jpg")
    train_labels = count_files(dataset_dir / "labels" / "train2017", "*.txt")
    val_labels = count_files(dataset_dir / "labels" / "val2017", "*.txt")

    print("\nCOCO 2017 preparado em:", dataset_dir)
    print(f"Treino:    {train_images:,} imagens / {train_labels:,} labels")
    print(f"Validação: {val_images:,} imagens / {val_labels:,} labels")

    if (train_images, val_images) != (118_287, 5_000):
        raise RuntimeError(
            "Download incompleto: eram esperadas 118.287 imagens de treino e "
            "5.000 imagens de validação. Execute novamente para completar."
        )
    log("Validação concluída: dataset completo e pronto para uso.")


def select_stratified_images(data: dict, limit: int, seed: int) -> list[int]:
    """Seleciona imagens garantindo uma cota inicial para cada classe COCO."""
    rng = random.Random(seed)
    category_images: dict[int, set[int]] = defaultdict(set)
    eligible_ids: set[int] = set()

    for annotation in data["annotations"]:
        if annotation.get("iscrowd", False):
            continue
        image_id = annotation["image_id"]
        eligible_ids.add(image_id)
        category_images[annotation["category_id"]].add(image_id)

    if limit > len(eligible_ids):
        raise ValueError(
            f"Limite {limit:,} excede as {len(eligible_ids):,} imagens anotadas disponíveis."
        )

    selected: set[int] = set()
    categories = sorted(category_images, key=lambda category: len(category_images[category]))
    quota = max(1, limit // len(categories))

    # Começar pelas classes raras evita que as frequentes consumam todo o limite.
    for category_id in categories:
        candidates = list(category_images[category_id] - selected)
        rng.shuffle(candidates)
        selected.update(candidates[: min(quota, limit - len(selected))])
        if len(selected) == limit:
            break

    remaining = list(eligible_ids - selected)
    rng.shuffle(remaining)
    selected.update(remaining[: limit - len(selected)])
    return sorted(selected)


def write_yolo_labels(data: dict, selected_ids: set[int], labels_dir: Path) -> None:
    """Converte bounding boxes COCO xywh para labels YOLO normalizados."""
    labels_dir.mkdir(parents=True, exist_ok=True)
    images = {image["id"]: image for image in data["images"] if image["id"] in selected_ids}
    category_map = {
        category_id: index
        for index, category_id in enumerate(sorted(c["id"] for c in data["categories"]))
    }
    annotations: dict[int, list[dict]] = defaultdict(list)
    for annotation in data["annotations"]:
        if annotation["image_id"] in selected_ids and not annotation.get("iscrowd", False):
            annotations[annotation["image_id"]].append(annotation)

    for image_id, image in images.items():
        lines: list[str] = []
        seen: set[tuple[float, ...]] = set()
        width, height = image["width"], image["height"]
        for annotation in annotations[image_id]:
            x, y, box_width, box_height = annotation["bbox"]
            if box_width <= 0 or box_height <= 0:
                continue
            values = (
                float(category_map[annotation["category_id"]]),
                (x + box_width / 2) / width,
                (y + box_height / 2) / height,
                box_width / width,
                box_height / height,
            )
            if values not in seen:
                seen.add(values)
                lines.append("%g %g %g %g %g" % values)
        (labels_dir / Path(image["file_name"]).with_suffix(".txt")).write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )


def download_one_image(image: dict, destination: Path) -> None:
    output = destination / image["file_name"]
    if output.exists() and output.stat().st_size > 0:
        return
    url = image.get("coco_url") or image["flickr_url"]
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            temporary = output.with_suffix(output.suffix + ".part")
            temporary.write_bytes(response.content)
            temporary.replace(output)
            return
        except (OSError, requests.RequestException):
            if attempt == 2:
                raise
            time.sleep(2**attempt)


def prepare_limited_coco(
    dataset_dir: Path, limit: int = 20_000, seed: int = 42, workers: int = 8
) -> None:
    """Baixa somente uma amostra estratificada do COCO e cria seus labels YOLO."""
    if limit < 80:
        raise ValueError("Use --limit com pelo menos 80 imagens para cobrir as 80 classes.")
    if workers < 1:
        raise ValueError("--workers deve ser maior que zero.")

    dataset_dir = dataset_dir.expanduser().resolve()
    dataset_dir.mkdir(parents=True, exist_ok=True)
    log(
        f"Iniciando preparação da amostra COCO com {limit:,} imagens em "
        f"{dataset_dir} (seed={seed}, workers={workers})"
    )
    download_and_extract(COCO_ANNOTATIONS_URL, dataset_dir)

    split_limits = {"train2017": limit - max(1, limit // 10), "val2017": max(1, limit // 10)}
    log(
        "Divisão planejada: "
        f"{split_limits['train2017']:,} treino / "
        f"{split_limits['val2017']:,} validação"
    )
    summary: dict[str, int] = {}

    for split, split_limit in split_limits.items():
        json_path = dataset_dir / "annotations" / f"instances_{split}.json"
        log(f"[{split}] Lendo anotações de {json_path} ...")
        with json_path.open("r", encoding="utf-8") as annotation_file:
            data = json.load(annotation_file)

        log(f"[{split}] Selecionando {split_limit:,} imagens de forma estratificada ...")
        selected = set(select_stratified_images(data, split_limit, seed))
        selected_images = [image for image in data["images"] if image["id"] in selected]
        images_dir = dataset_dir / "images" / split
        labels_dir = dataset_dir / "labels" / split
        images_dir.mkdir(parents=True, exist_ok=True)
        log(f"[{split}] Gerando {len(selected_images):,} arquivos de labels YOLO ...")
        write_yolo_labels(data, selected, labels_dir)
        log(f"[{split}] Labels gerados em {labels_dir}")

        failures: list[str] = []
        existing_images = sum(
            1
            for image in selected_images
            if (images_dir / image["file_name"]).is_file()
            and (images_dir / image["file_name"]).stat().st_size > 0
        )
        log(
            f"[{split}] Baixando imagens com {workers} workers "
            f"({existing_images:,} já existentes serão reutilizadas) ..."
        )
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(download_one_image, image, images_dir): image["file_name"]
                for image in selected_images
            }
            for future in TQDM(
                as_completed(futures), total=len(futures), desc=f"Imagens {split}"
            ):
                try:
                    future.result()
                except Exception:
                    failures.append(futures[future])

        if failures:
            raise RuntimeError(
                f"Falha ao baixar {len(failures)} imagens de {split}. "
                "Execute novamente para tentar completar. Exemplos: " + ", ".join(failures[:5])
            )
        summary[split] = len(selected_images)
        log(f"[{split}] Processamento concluído: {len(selected_images):,} imagens.")

    names = {
        index: category["name"]
        for index, category in enumerate(sorted(data["categories"], key=lambda item: item["id"]))
    }
    yaml_data = {
        "path": str(dataset_dir),
        "train": "images/train2017",
        "val": "images/val2017",
        "nc": 80,
        "names": names,
    }
    yaml_path = dataset_dir / "coco20k.yaml"
    log(f"Gerando configuração do dataset em {yaml_path} ...")
    yaml_path.write_text(
        yaml.safe_dump(yaml_data, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(f"\nCOCO limitado preparado em {dataset_dir}")
    print(f"Treino: {summary['train2017']:,} imagens")
    print(f"Validação: {summary['val2017']:,} imagens")
    log("Amostra limitada pronta para uso.")

if __name__ == "__main__":
    args = parse_args()
    log("Argumentos recebidos; iniciando execução.")
    if args.limit is not None:
        limited_dir = args.dataset_dir
        if limited_dir == DEFAULT_DATASET_DIR:
            limited_dir = DEFAULT_LIMITED_DIR
        prepare_limited_coco(limited_dir, args.limit, args.seed, args.workers)
    else:
        download_coco(args.dataset_dir, args.include_test)
