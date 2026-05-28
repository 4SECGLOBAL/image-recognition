from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "Inferencia" / "resultado.jpg"


class Detection(BaseModel):
    indice: int
    classe_id: int
    classe: str
    confianca: float
    confianca_percentual: float
    bbox_xyxy: list[float]


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


class InferenciaResponse(BaseModel):
    model: str
    image: str
    output: str
    resultado_url: str
    confianca_minima: float
    total_deteccoes: int
    deteccoes: list[Detection]
    velocidade_ms: dict[str, float]


router = APIRouter(prefix="/api/4/inferencia", tags=["Inferencia"])


def resolver_caminho(caminho: str) -> Path:
    path = Path(caminho)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def caminho_relativo(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def montar_resultado_url(request: Request, output_file: Path) -> str:
    rel_path = output_file.relative_to(REPO_ROOT / "Inferencia")
    return str(request.url_for("inferencia_files", path=str(rel_path)))


def executar_inferencia(payload: InferenciaRequest, resultado_url: str) -> InferenciaResponse:
    model_file = resolver_caminho(payload.model)
    image_file = resolver_caminho(payload.image)
    output_file = DEFAULT_OUTPUT

    if not model_file.exists():
        raise HTTPException(status_code=400, detail=f"Modelo nao encontrado: {model_file}")
    if not image_file.exists():
        raise HTTPException(status_code=400, detail=f"Imagem nao encontrada: {image_file}")

    model = YOLO(str(model_file))
    results = model(str(image_file), conf=payload.confianca)
    result = results[0]

    deteccoes = []
    if result.boxes is not None:
        for indice, box in enumerate(result.boxes, start=1):
            classe_id = int(box.cls.item())
            confianca = float(box.conf.item())
            deteccoes.append(
                Detection(
                    indice=indice,
                    classe_id=classe_id,
                    classe=result.names[classe_id],
                    confianca=confianca,
                    confianca_percentual=round(confianca * 100, 2),
                    bbox_xyxy=[round(float(value), 2) for value in box.xyxy[0].tolist()],
                )
            )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    result.save(filename=str(output_file))

    return InferenciaResponse(
        model=caminho_relativo(model_file),
        image=caminho_relativo(image_file),
        output=caminho_relativo(output_file),
        resultado_url=resultado_url,
        confianca_minima=payload.confianca,
        total_deteccoes=len(deteccoes),
        deteccoes=deteccoes,
        velocidade_ms={key: round(float(value), 2) for key, value in result.speed.items()},
    )


@router.post("/", response_model=InferenciaResponse)
async def inferir(payload: InferenciaRequest, request: Request) -> InferenciaResponse:
    resultado_url = montar_resultado_url(request, DEFAULT_OUTPUT)
    return await run_in_threadpool(executar_inferencia, payload, resultado_url)
