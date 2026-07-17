from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from ultralytics import YOLO

from Inferencia.api.matrix_confusion import YoloBox, generate_confusion_matrix

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "Inferencia" / "resultado.jpg"
DEFAULT_CONFUSION_MATRIX_OUTPUT = REPO_ROOT / "Inferencia" / "matriz_confusao.jpg"


class Detection(BaseModel):
    indice: int
    classe_id: int
    classe: str
    confianca: float
    confianca_percentual: float
    bbox_xyxy: list[float]


class ConfusionMatrixResponse(BaseModel):
    output: str | None
    url: str | None
    label: str | None
    data_yaml: str
    status: str
    iou_threshold: float
    classes: list[str]
    matrix: list[list[int]]
    matched: int
    false_positives: int
    false_negatives: int


class InferenciaRequest(BaseModel):
    model: str = Field(
        default="runs/detect/train-11/weights/best.pt",
        description="Caminho do modelo YOLO .pt.",
        examples=["runs/detect/train-11/weights/best.pt"],
    )
    image: str = Field(
        default="Inferencia/foto3.jpg",
        description="Caminho da imagem de entrada.",
        examples=["Inferencia/foto3.jpg"],
    )
    confianca: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Confianca minima da predicao, entre 0.0 e 1.0.",
        examples=[0.05],
    )
    data_yaml: str = Field(
        default="Avaliador/data.yaml",
        description="Caminho do data.yaml com os nomes das classes YOLO.",
        examples=["Avaliador/data.yaml"],
    )
    label: str | None = Field(
        default=None,
        description=(
            "Caminho opcional do .txt YOLO ground truth. Se vazio, a API procura um .txt "
            "com o mesmo nome da imagem em Inferencia, Avaliador/labels/train, "
            "Avaliador/labels/val e Avaliador/test/labels."
        ),
        examples=["Avaliador/test/labels/foto3.txt"],
    )
    iou_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="IoU minimo para considerar uma predicao correspondente a uma anotacao real.",
        examples=[0.5],
    )


class InferenciaResponse(BaseModel):
    model: str
    image: str
    output: str
    resultado_url: str
    confianca_minima: float
    total_deteccoes: int
    deteccoes: list[Detection]
    velocidade_ms: dict[str, float]
    matriz_confusao: ConfusionMatrixResponse


router = APIRouter(prefix="/api/4/inferencia", tags=["Inferencia"])


def resolver_caminho(caminho: str) -> Path:
    path = Path(caminho)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def caminho_relativo(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def montar_arquivo_url(request: Request, output_file: Path) -> str:
    rel_path = output_file.relative_to(REPO_ROOT / "Inferencia")
    return str(request.url_for("inferencia_files", path=str(rel_path)))


def executar_inferencia(payload: InferenciaRequest, resultado_url: str, matriz_confusao_url: str) -> InferenciaResponse:
    model_file = resolver_caminho(payload.model)
    image_file = resolver_caminho(payload.image)
    data_yaml_file = resolver_caminho(payload.data_yaml)
    label_file = resolver_caminho(payload.label) if payload.label else None
    output_file = DEFAULT_OUTPUT
    matriz_confusao_file = DEFAULT_CONFUSION_MATRIX_OUTPUT

    if not model_file.exists():
        raise HTTPException(status_code=400, detail=f"Modelo nao encontrado: {model_file}")
    if not image_file.exists():
        raise HTTPException(status_code=400, detail=f"Imagem nao encontrada: {image_file}")
    if not data_yaml_file.exists():
        raise HTTPException(status_code=400, detail=f"data.yaml nao encontrado: {data_yaml_file}")
    if label_file is not None and not label_file.exists():
        raise HTTPException(status_code=400, detail=f"Label nao encontrado: {label_file}")

    model = YOLO(str(model_file))
    results = model(str(image_file), conf=payload.confianca)
    result = results[0]

    deteccoes = []
    prediction_boxes = []
    if result.boxes is not None:
        for indice, box in enumerate(result.boxes, start=1):
            classe_id = int(box.cls.item())
            confianca = float(box.conf.item())
            bbox_xyxy = [round(float(value), 2) for value in box.xyxy[0].tolist()]
            deteccoes.append(
                Detection(
                    indice=indice,
                    classe_id=classe_id,
                    classe=result.names[classe_id],
                    confianca=confianca,
                    confianca_percentual=round(confianca * 100, 2),
                    bbox_xyxy=bbox_xyxy,
                )
            )
            prediction_boxes.append(YoloBox(class_id=classe_id, xyxy=tuple(bbox_xyxy)))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    result.save(filename=str(output_file))

    try:
        matriz_result = generate_confusion_matrix(
            data_yaml=data_yaml_file,
            image_file=image_file,
            explicit_label=label_file,
            predictions=prediction_boxes,
            output_file=matriz_confusao_file,
            repo_root=REPO_ROOT,
            iou_threshold=payload.iou_threshold,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if matriz_result is None:
        matriz_confusao = ConfusionMatrixResponse(
            output=None,
            url=None,
            label=None,
            data_yaml=caminho_relativo(data_yaml_file),
            status="label_ground_truth_nao_encontrado",
            iou_threshold=payload.iou_threshold,
            classes=[],
            matrix=[],
            matched=0,
            false_positives=0,
            false_negatives=0,
        )
    else:
        matriz_confusao = ConfusionMatrixResponse(
            output=caminho_relativo(matriz_result.output_file),
            url=matriz_confusao_url,
            label=caminho_relativo(matriz_result.label_file),
            data_yaml=caminho_relativo(data_yaml_file),
            status="gerada",
            iou_threshold=matriz_result.iou_threshold,
            classes=matriz_result.classes,
            matrix=matriz_result.matrix,
            matched=matriz_result.matched,
            false_positives=matriz_result.false_positives,
            false_negatives=matriz_result.false_negatives,
        )

    return InferenciaResponse(
        model=caminho_relativo(model_file),
        image=caminho_relativo(image_file),
        output=caminho_relativo(output_file),
        resultado_url=resultado_url,
        confianca_minima=payload.confianca,
        total_deteccoes=len(deteccoes),
        deteccoes=deteccoes,
        velocidade_ms={key: round(float(value), 2) for key, value in result.speed.items()},
        matriz_confusao=matriz_confusao,
    )


@router.post("/", response_model=InferenciaResponse)
async def inferir(payload: InferenciaRequest, request: Request) -> InferenciaResponse:
    resultado_url = montar_arquivo_url(request, DEFAULT_OUTPUT)
    matriz_confusao_url = montar_arquivo_url(request, DEFAULT_CONFUSION_MATRIX_OUTPUT)
    return await run_in_threadpool(executar_inferencia, payload, resultado_url, matriz_confusao_url)
