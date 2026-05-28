from __future__ import annotations

import random
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool


REPO_ROOT = Path(__file__).resolve().parents[2]
YOLO_EXEC = REPO_ROOT / "env_model" / "bin" / "yolo"
AUTO_ANNOTATE_LABELS_DIR = REPO_ROOT / "DataScrapper" / "images_auto_annotate_labels"
AVALIADOR_DIR = REPO_ROOT / "Avaliador"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".avif"}


class TrainRequest(BaseModel):
    data: str = Field(default="Avaliador/data.yaml", description="Caminho do data.yaml do dataset.")
    model: str = Field(default="yolov8n.pt", description="Modelo base ou pesos .pt para iniciar o treino.")
    epochs: int = Field(default=1, ge=1, description="Numero de epocas do treinamento.")
    batch: int = Field(default=4, ge=1, description="Tamanho do batch.")
    imgsz: int = Field(default=640, ge=1, description="Tamanho das imagens de entrada.")
    device: str = Field(default="0", description="Dispositivo de treino. Exemplos: 0, cpu.")
    cache: bool = Field(default=False, description="Se true, habilita cache do dataset no YOLO.")
    workers: int = Field(
        default=0,
        ge=0,
        description="Quantidade de dataloader workers. Use 0 para evitar erro de shared memory em Docker.",
    )


class TrainResponse(BaseModel):
    comando: list[str]
    data: str
    model: str
    returncode: int
    runs_dir: str


class DistributeRequest(BaseModel):
    data: str | None = Field(
        default=None,
        description="Data no formato YYYY-MM-DD. Se vazio, usa a data de hoje.",
        examples=["2026-05-26"],
    )


class SplitCount(BaseModel):
    images: int
    labels: int


class DistributeResponse(BaseModel):
    data: str
    source_dir: str
    total_pairs: int
    train: SplitCount
    val: SplitCount
    test: SplitCount


router = APIRouter(prefix="/api/3/evaluator", tags=["Avaliador"])


def resolver_caminho(caminho: str) -> Path:
    path = Path(caminho)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def caminho_relativo(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def data_hoje() -> str:
    return datetime.now(timezone(timedelta(hours=-3))).date().isoformat()


def normalizar_data(data: str | None) -> str:
    data_normalizada = (data or "").strip() or data_hoje()
    try:
        datetime.strptime(data_normalizada, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Data invalida. Use o formato YYYY-MM-DD.") from exc
    return data_normalizada


def montar_comando(payload: TrainRequest) -> tuple[list[str], Path, Path]:
    data_path = resolver_caminho(payload.data)
    model_path = resolver_caminho(payload.model)

    comando = [
        str(YOLO_EXEC),
        "train",
        f"data={data_path}",
        f"model={model_path}",
        f"epochs={payload.epochs}",
        f"batch={payload.batch}",
        f"imgsz={payload.imgsz}",
        f"device={payload.device}",
        f"cache={str(payload.cache)}",
        f"workers={payload.workers}",
    ]

    return comando, data_path, model_path


def validar_device(device: str) -> None:
    if device.strip().lower() == "cpu":
        return

    codigo = (
        "import torch; "
        "print(torch.cuda.is_available()); "
        "print(torch.cuda.device_count())"
    )
    resultado = subprocess.run(
        [str(REPO_ROOT / "env_model" / "bin" / "python"), "-c", codigo],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    linhas = [linha.strip() for linha in resultado.stdout.splitlines() if linha.strip()]
    cuda_disponivel = linhas[0] == "True" if linhas else False
    device_count = int(linhas[1]) if len(linhas) > 1 and linhas[1].isdigit() else 0

    if not cuda_disponivel or device_count == 0:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Device CUDA solicitado ({device}), mas o container nao enxerga GPU. "
                "Use device='cpu' ou recrie o evaluator-api com GPU habilitada."
            ),
        )


def normalizar_data_yaml(data_path: Path) -> None:
    with data_path.open("r", encoding="utf-8") as data_file:
        data = yaml.safe_load(data_file) or {}

    data["path"] = str(REPO_ROOT / "Avaliador")
    data.setdefault("train", "images/train")
    data.setdefault("val", "images/val")
    data.setdefault("test", "test/images")

    names = data.get("names") or {}
    if isinstance(names, list):
        names = {index: name for index, name in enumerate(names)}
    if names:
        data["names"] = names
        data.setdefault("nc", len(names))

    with data_path.open("w", encoding="utf-8") as data_file:
        yaml.safe_dump(data, data_file, allow_unicode=True, sort_keys=False)


def listar_pares_anotados(source_dir: Path) -> list[tuple[Path, Path]]:
    imagens = sorted(path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)
    pares: list[tuple[Path, Path]] = []
    sem_label: list[str] = []

    for image_path in imagens:
        label_path = image_path.with_suffix(".txt")
        if label_path.exists() and label_path.is_file():
            pares.append((image_path, label_path))
        else:
            sem_label.append(image_path.name)

    if sem_label:
        exemplos = ", ".join(sem_label[:10])
        raise HTTPException(status_code=400, detail=f"Imagens sem label correspondente: {exemplos}")
    if not pares:
        raise HTTPException(status_code=400, detail=f"Nenhum par imagem/label encontrado em: {source_dir}")

    return pares


def preparar_diretorio(destino: Path, extensoes: set[str]) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    for path in destino.iterdir():
        if path.is_file() and path.suffix.lower() in extensoes:
            path.unlink()


def copiar_split(pares: list[tuple[Path, Path]], images_dir: Path, labels_dir: Path) -> SplitCount:
    preparar_diretorio(images_dir, IMAGE_EXTENSIONS)
    preparar_diretorio(labels_dir, {".txt"})

    for image_path, label_path in pares:
        shutil.copy2(image_path, images_dir / image_path.name)
        shutil.copy2(label_path, labels_dir / label_path.name)

    return SplitCount(images=len(pares), labels=len(pares))


def executar_distribuicao(payload: DistributeRequest) -> DistributeResponse:
    data = normalizar_data(payload.data)
    source_dir = AUTO_ANNOTATE_LABELS_DIR / data

    if not source_dir.exists() or not source_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Pasta de anotacoes nao encontrada: {source_dir}")

    pares = listar_pares_anotados(source_dir)
    random.Random(42).shuffle(pares)

    total = len(pares)
    train_count = int(total * 0.70)
    val_count = int(total * 0.20)
    test_count = total - train_count - val_count

    train_pairs = pares[:train_count]
    val_pairs = pares[train_count : train_count + val_count]
    test_pairs = pares[train_count + val_count : train_count + val_count + test_count]

    train = copiar_split(train_pairs, AVALIADOR_DIR / "images" / "train", AVALIADOR_DIR / "labels" / "train")
    val = copiar_split(val_pairs, AVALIADOR_DIR / "images" / "val", AVALIADOR_DIR / "labels" / "val")
    test = copiar_split(test_pairs, AVALIADOR_DIR / "test" / "images", AVALIADOR_DIR / "test" / "labels")

    return DistributeResponse(
        data=data,
        source_dir=caminho_relativo(source_dir),
        total_pairs=total,
        train=train,
        val=val,
        test=test,
    )


def executar_treino(payload: TrainRequest) -> TrainResponse:
    comando, data_path, model_path = montar_comando(payload)

    if not data_path.exists():
        raise HTTPException(status_code=400, detail=f"data.yaml nao encontrado: {data_path}")
    if not model_path.exists():
        raise HTTPException(status_code=400, detail=f"Modelo nao encontrado: {model_path}")
    validar_device(payload.device)

    normalizar_data_yaml(data_path)

    processo = subprocess.Popen(
        comando,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
    )

    def encaminhar_stdout() -> None:
        if processo.stdout is None:
            return
        for linha in processo.stdout:
            sys.stdout.write(linha)
            sys.stdout.flush()

    def encaminhar_stderr() -> None:
        if processo.stderr is None:
            return
        for linha in processo.stderr:
            sys.stderr.write(linha)
            sys.stderr.flush()

    stdout_thread = threading.Thread(target=encaminhar_stdout)
    stderr_thread = threading.Thread(target=encaminhar_stderr)
    stdout_thread.start()
    stderr_thread.start()

    returncode = processo.wait()
    stdout_thread.join()
    stderr_thread.join()

    response = TrainResponse(
        comando=comando,
        data=caminho_relativo(data_path),
        model=caminho_relativo(model_path),
        returncode=returncode,
        runs_dir="runs/detect",
    )

    if returncode != 0:
        raise HTTPException(status_code=500, detail=response.model_dump())

    return response


@router.post("/train", response_model=TrainResponse)
async def treinar(payload: TrainRequest) -> TrainResponse:
    return await run_in_threadpool(executar_treino, payload)


@router.post("/distribute", response_model=DistributeResponse)
async def distribuir(payload: DistributeRequest) -> DistributeResponse:
    return await run_in_threadpool(executar_distribuicao, payload)
