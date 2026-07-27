from __future__ import annotations

import random
import shutil
import subprocess
import sys
import threading
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException
from PIL import Image, UnidentifiedImageError
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


class EvaluationRequest(BaseModel):
    data: str = Field(default="Avaliador/data.yaml", description="Caminho do data.yaml do dataset.")
    model: str = Field(default="best.pt", description="Caminho dos pesos .pt que serao avaliados.")
    test_path: str = Field(
        default="Avaliador/test",
        description="Pasta do conjunto de teste, contendo labels e images_auto_annotate_labels.",
    )
    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Limiar de confianca opcional usado pelo YOLO.",
    )
    device: str | None = Field(default=None, description="Dispositivo opcional. Exemplos: 0, cpu.")
    save_json: bool | None = Field(default=None, description="Se definido, controla a exportacao JSON do YOLO.")


class EvaluationResponse(BaseModel):
    comando: list[str]
    data: str
    model: str
    test_path: str
    returncode: int
    validation_dir: str = Field(description="Pasta dos resultados relativa a raiz do projeto.")
    validation_dir_absoluto: str = Field(description="Pasta dos resultados dentro do evaluator-api.")
    artefatos_gerados: list[str] = Field(description="Arquivos criados ou atualizados nesta avaliacao.")
    matriz_confusao: str | None = Field(description="Caminho da matriz de confusao absoluta.")
    matriz_confusao_normalizada: str | None = Field(description="Caminho da matriz de confusao normalizada.")
    assertivity_file: str | None = Field(description="Caminho do relatorio de assertividade por classe.")


class DistributeRequest(BaseModel):
    data: str | None = Field(
        default=None,
        description=(
            "Nome da pasta usada para buscar "
            "DataScrapper/images_auto_annotate_labels/<data>. "
            "Se vazio, usa a data de hoje no fuso UTC-3."
        ),
        examples=["dataset-projeto"],
    )


class SplitCount(BaseModel):
    images: int = Field(description="Quantidade de imagens copiadas para o split.")
    labels: int = Field(description="Quantidade de labels copiadas para o split.")


class DistributeResponse(BaseModel):
    data: str = Field(description="Data usada para localizar a pasta de origem.")
    source_dir: str = Field(description="Pasta de origem com os pares imagem+label.")
    total_pairs: int = Field(description="Total de pares imagem+label encontrados.")
    train: SplitCount = Field(description="Arquivos copiados para Avaliador/images/train e Avaliador/labels/train.")
    val: SplitCount = Field(description="Arquivos copiados para Avaliador/images/val e Avaliador/labels/val.")
    test: SplitCount = Field(description="Arquivos copiados para Avaliador/test/images e Avaliador/test/labels.")


class ClassImageInstance(BaseModel):
    split: str = Field(description="Split do dataset: train, val ou test.")
    image: str = Field(description="Nome da imagem correspondente ao arquivo de anotacao.")
    label: str = Field(description="Nome do arquivo .txt de anotacao.")
    instances: int = Field(description="Quantidade de anotacoes desta classe nesta imagem.")


class ClassSplitSummary(BaseModel):
    annotations: int = Field(description="Quantidade de anotacoes da classe no split.")
    images: int = Field(description="Quantidade de imagens que possuem pelo menos uma anotacao da classe no split.")


class ClassAnnotationSummary(BaseModel):
    id: int = Field(description="ID numerico da classe YOLO.")
    name: str = Field(description="Nome da classe definido no data.yaml.")
    annotations: int = Field(description="Quantidade total de anotacoes da classe.")
    images: int = Field(description="Quantidade total de imagens que possuem pelo menos uma anotacao da classe.")
    splits: dict[str, ClassSplitSummary] = Field(description="Resumo por split.")
    instances_by_image: list[ClassImageInstance] = Field(
        description="Para cada imagem em que a classe aparece, quantas instancias foram anotadas."
    )


class EvaluatorDatasetSummary(BaseModel):
    data_yaml: str = Field(description="Caminho do data.yaml lido.")
    label_dirs: dict[str, str] = Field(description="Pastas de labels analisadas por split.")
    total_label_files: int = Field(description="Quantidade total de arquivos .txt lidos.")
    classes: list[ClassAnnotationSummary] = Field(description="Resumo das anotacoes para cada classe YOLO.")
    unknown_annotations: dict[int, int] = Field(
        description="Anotacoes encontradas para IDs de classe que nao existem no data.yaml."
    )


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
    nome_pasta = (data or "").strip() or data_hoje()
    if nome_pasta in {".", ".."} or Path(nome_pasta).name != nome_pasta or "\\" in nome_pasta or "\0" in nome_pasta:
        raise HTTPException(status_code=400, detail="Nome de pasta invalido.")
    return nome_pasta


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


def montar_comando_avaliacao(
    payload: EvaluationRequest,
) -> tuple[list[str], Path, Path, Path]:
    data_path = resolver_caminho(payload.data)
    model_path = resolver_caminho(payload.model)
    test_path = resolver_caminho(payload.test_path)

    comando = [
        "/bin/bash",
        str(REPO_ROOT / "avaliacao.sh"),
        str(data_path),
        str(model_path),
        str(test_path),
        "" if payload.confidence is None else str(payload.confidence),
        "" if payload.device is None else payload.device,
        "" if payload.save_json is None else str(payload.save_json),
    ]
    return comando, data_path, model_path, test_path


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


def carregar_classes_yolo(data_path: Path) -> dict[int, str]:
    if not data_path.exists():
        raise HTTPException(status_code=400, detail=f"data.yaml nao encontrado: {data_path}")

    with data_path.open("r", encoding="utf-8") as data_file:
        data = yaml.safe_load(data_file) or {}

    names = data.get("names") or {}
    if isinstance(names, list):
        return {index: str(name) for index, name in enumerate(names)}

    if isinstance(names, dict):
        try:
            return {int(class_id): str(name) for class_id, name in names.items()}
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="IDs de classe invalidos em data.yaml.") from exc

    raise HTTPException(status_code=400, detail="Campo names invalido ou ausente em data.yaml.")


def ler_classe_anotacao(label_path: Path, line_number: int, line: str) -> int:
    parts = line.split()
    if not parts:
        raise HTTPException(
            status_code=400,
            detail=f"Anotacao invalida em {caminho_relativo(label_path)}:{line_number}.",
        )

    try:
        return int(parts[0])
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Classe YOLO invalida em {caminho_relativo(label_path)}:{line_number}.",
        ) from exc


def localizar_imagem(image_dir: Path, label_path: Path) -> str:
    base_name = label_path.with_suffix("").name
    for extension in IMAGE_EXTENSIONS:
        image_path = image_dir / f"{base_name}{extension}"
        if image_path.exists():
            return image_path.name
    return base_name


def executar_resumo_dataset() -> EvaluatorDatasetSummary:
    data_path = AVALIADOR_DIR / "data.yaml"
    classes = carregar_classes_yolo(data_path)
    label_dirs = {
        "train": AVALIADOR_DIR / "labels" / "train",
        "val": AVALIADOR_DIR / "labels" / "val",
        "test": AVALIADOR_DIR / "test" / "labels",
    }
    image_dirs = {
        "train": AVALIADOR_DIR / "images" / "train",
        "val": AVALIADOR_DIR / "images" / "val",
        "test": AVALIADOR_DIR / "test" / "images",
    }

    annotations_by_class: Counter[int] = Counter()
    images_by_class: dict[int, set[str]] = defaultdict(set)
    annotations_by_split_class: dict[str, Counter[int]] = defaultdict(Counter)
    images_by_split_class: dict[str, dict[int, set[str]]] = defaultdict(lambda: defaultdict(set))
    instances_by_class_image: dict[int, list[ClassImageInstance]] = defaultdict(list)
    unknown_annotations: Counter[int] = Counter()
    total_label_files = 0

    for split, label_dir in label_dirs.items():
        if not label_dir.exists():
            continue

        for label_path in sorted(label_dir.glob("*.txt")):
            total_label_files += 1
            image_name = localizar_imagem(image_dirs[split], label_path)
            class_counts: Counter[int] = Counter()

            with label_path.open("r", encoding="utf-8") as label_file:
                for line_number, raw_line in enumerate(label_file, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue

                    class_id = ler_classe_anotacao(label_path, line_number, line)
                    class_counts[class_id] += 1

            for class_id, instances in class_counts.items():
                if class_id not in classes:
                    unknown_annotations[class_id] += instances
                    continue

                annotations_by_class[class_id] += instances
                images_by_class[class_id].add(f"{split}/{image_name}")
                annotations_by_split_class[split][class_id] += instances
                images_by_split_class[split][class_id].add(image_name)
                instances_by_class_image[class_id].append(
                    ClassImageInstance(
                        split=split,
                        image=image_name,
                        label=label_path.name,
                        instances=instances,
                    )
                )

    summaries = []
    for class_id, name in sorted(classes.items()):
        splits = {
            split: ClassSplitSummary(
                annotations=annotations_by_split_class[split][class_id],
                images=len(images_by_split_class[split][class_id]),
            )
            for split in label_dirs
        }
        summaries.append(
            ClassAnnotationSummary(
                id=class_id,
                name=name,
                annotations=annotations_by_class[class_id],
                images=len(images_by_class[class_id]),
                splits=splits,
                instances_by_image=instances_by_class_image[class_id],
            )
        )

    return EvaluatorDatasetSummary(
        data_yaml=caminho_relativo(data_path),
        label_dirs={split: caminho_relativo(path) for split, path in label_dirs.items()},
        total_label_files=total_label_files,
        classes=summaries,
        unknown_annotations=dict(sorted(unknown_annotations.items())),
    )


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


def identificar_imagens_avif(pares: list[tuple[Path, Path]]) -> set[Path]:
    imagens_avif: set[Path] = set()

    for image_path, _ in pares:
        try:
            with Image.open(image_path) as image:
                if (image.format or "").upper() == "AVIF":
                    image.load()
                    imagens_avif.add(image_path)
        except (OSError, UnidentifiedImageError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Imagem invalida ou nao suportada: {image_path.name}",
            ) from exc

    return imagens_avif


def converter_avif_para_jpeg(origem: Path, destino: Path) -> None:
    with Image.open(origem) as image:
        if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
            rgba = image.convert("RGBA")
            rgb = Image.new("RGB", rgba.size, "white")
            rgb.paste(rgba, mask=rgba.getchannel("A"))
        else:
            rgb = image.convert("RGB")

        rgb.save(destino, format="JPEG", quality=95, subsampling=0)


def limpar_cache_yolo(labels_dir: Path) -> None:
    cache_path = labels_dir.parent / f"{labels_dir.name}.cache"
    cache_path.unlink(missing_ok=True)


def copiar_split(
    pares: list[tuple[Path, Path]],
    images_dir: Path,
    labels_dir: Path,
    imagens_avif: set[Path],
) -> SplitCount:
    preparar_diretorio(images_dir, IMAGE_EXTENSIONS)
    preparar_diretorio(labels_dir, {".txt"})
    limpar_cache_yolo(labels_dir)

    for image_path, label_path in pares:
        if image_path in imagens_avif:
            converter_avif_para_jpeg(image_path, images_dir / f"{image_path.stem}.jpg")
        else:
            shutil.copy2(image_path, images_dir / image_path.name)
        shutil.copy2(label_path, labels_dir / label_path.name)

    return SplitCount(images=len(pares), labels=len(pares))


def executar_distribuicao(payload: DistributeRequest) -> DistributeResponse:
    data = normalizar_data(payload.data)
    source_dir = AUTO_ANNOTATE_LABELS_DIR / data

    if not source_dir.exists() or not source_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Pasta de anotacoes nao encontrada: {source_dir}")

    pares = listar_pares_anotados(source_dir)
    imagens_avif = identificar_imagens_avif(pares)
    random.Random(42).shuffle(pares)

    total = len(pares)
    train_count = int(total * 0.70)
    val_count = int(total * 0.20)
    test_count = total - train_count - val_count

    train_pairs = pares[:train_count]
    val_pairs = pares[train_count : train_count + val_count]
    test_pairs = pares[train_count + val_count : train_count + val_count + test_count]

    train = copiar_split(
        train_pairs,
        AVALIADOR_DIR / "images" / "train",
        AVALIADOR_DIR / "labels" / "train",
        imagens_avif,
    )
    val = copiar_split(
        val_pairs,
        AVALIADOR_DIR / "images" / "val",
        AVALIADOR_DIR / "labels" / "val",
        imagens_avif,
    )
    test = copiar_split(
        test_pairs,
        AVALIADOR_DIR / "test" / "images",
        AVALIADOR_DIR / "test" / "labels",
        imagens_avif,
    )

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


def executar_avaliacao(payload: EvaluationRequest) -> EvaluationResponse:
    comando, data_path, model_path, test_path = montar_comando_avaliacao(payload)
    validation_dir = AVALIADOR_DIR / "validacao"

    if not data_path.is_file():
        raise HTTPException(status_code=400, detail=f"data.yaml nao encontrado: {data_path}")
    if not model_path.is_file():
        raise HTTPException(status_code=400, detail=f"Modelo nao encontrado: {model_path}")
    if not test_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Pasta de teste nao encontrada: {test_path}")
    if not (test_path / "labels").is_dir():
        raise HTTPException(status_code=400, detail=f"Pasta de labels nao encontrada: {test_path / 'labels'}")
    if payload.device:
        validar_device(payload.device)

    normalizar_data_yaml(data_path)
    validation_dir.mkdir(parents=True, exist_ok=True)
    artefatos_antes = {
        path: (path.stat().st_mtime_ns, path.stat().st_size)
        for path in validation_dir.rglob("*")
        if path.is_file()
    }

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

    artefatos_depois = sorted(path for path in validation_dir.rglob("*") if path.is_file())
    artefatos_gerados_paths = [
        path
        for path in artefatos_depois
        if path not in artefatos_antes
        or (path.stat().st_mtime_ns, path.stat().st_size) != artefatos_antes[path]
    ]

    def localizar_artefato(nome: str) -> str | None:
        candidatos = [path for path in artefatos_gerados_paths if path.name == nome]
        return caminho_relativo(candidatos[-1]) if candidatos else None

    response = EvaluationResponse(
        comando=comando,
        data=caminho_relativo(data_path),
        model=caminho_relativo(model_path),
        test_path=caminho_relativo(test_path),
        returncode=returncode,
        validation_dir=caminho_relativo(validation_dir),
        validation_dir_absoluto=str(validation_dir),
        artefatos_gerados=[caminho_relativo(path) for path in artefatos_gerados_paths],
        matriz_confusao=localizar_artefato("confusion_matrix.png"),
        matriz_confusao_normalizada=localizar_artefato("confusion_matrix_normalized.png"),
        assertivity_file=localizar_artefato("assertivity.txt"),
    )

    if returncode != 0:
        raise HTTPException(status_code=500, detail=response.model_dump())

    return response


@router.get("/", response_model=EvaluatorDatasetSummary)
async def resumo_dataset() -> EvaluatorDatasetSummary:
    return await run_in_threadpool(executar_resumo_dataset)


@router.post("/train", response_model=TrainResponse)
async def treinar(payload: TrainRequest) -> TrainResponse:
    return await run_in_threadpool(executar_treino, payload)


@router.post(
    "/evaluate",
    response_model=EvaluationResponse,
    summary="Avalia o modelo YOLO no conjunto de teste",
)
async def avaliar(payload: EvaluationRequest) -> EvaluationResponse:
    return await run_in_threadpool(executar_avaliacao, payload)


@router.post(
    "/distribute",
    response_model=DistributeResponse,
    summary="Distribui imagens anotadas no dataset YOLO",
    description=(
        "Monta o dataset do Avaliador a partir dos pares imagem+label em "
        "`DataScrapper/images_auto_annotate_labels/<data>`. "
        "Recebe opcionalmente `data` com o nome da pasta (por exemplo, "
        "`dataset-projeto`); se não for enviada, usa a data de hoje no fuso UTC-3. "
        "Cada imagem precisa ter um `.txt` com "
        "o mesmo nome base, por exemplo `foto.jpg` e `foto.txt`. "
        "Após validar os pares, embaralha com seed fixa `42` e copia 70% para "
        "`Avaliador/images/train` + `Avaliador/labels/train`, 20% para "
        "`Avaliador/images/val` + `Avaliador/labels/val`, e 10% para "
        "`Avaliador/test/images` + `Avaliador/test/labels`. "
        "Antes da cópia, limpa das pastas de destino os arquivos antigos de "
        "imagem e label correspondentes e os caches YOLO. Imagens cujo conteúdo "
        "é AVIF são convertidas para JPEG mantendo dimensões e nome-base. "
        "Retorna o nome de pasta usado, a pasta de "
        "origem, o total de pares e as contagens por split. Retorna 400 quando "
        "existem imagens sem label correspondente e 404 quando a pasta informada "
        "não existe."
    ),
)
async def distribuir(payload: DistributeRequest) -> DistributeResponse:
    return await run_in_threadpool(executar_distribuicao, payload)
