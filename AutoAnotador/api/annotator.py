from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_EXEC = REPO_ROOT / "env_model" / "bin" / "python"
SCRIPT_PATH = REPO_ROOT / "AutoAnotador" / "annotator.py"


class AnnotatorRequest(BaseModel):
    diretorio: str = Field(
        default="./DataScrapper/images/",
        description="Diretorio ou arquivo .txt com as imagens para anotar.",
        examples=["./DataScrapper/images/"],
    )
    model: str = Field(
        default="yolov8n.pt",
        description="Caminho ou nome do modelo YOLO usado na anotacao.",
        examples=["yolov8n.pt"],
    )
    device: str = Field(
        default="0",
        description="Dispositivo para rodar o modelo. Exemplos: cpu, cuda, 0.",
        examples=["0"],
    )
    output_dir: str = Field(
        default="./DataScrapper/images_auto_annotate_labels",
        description="Diretorio para salvar os labels.",
        examples=["./DataScrapper/images_auto_annotate_labels"],
    )
    desired_class_id: int | None = Field(
        default=None,
        description="ID da classe para anotar. Se omitido, anota todas as classes detectadas.",
        examples=[0],
    )
    draw: bool = Field(
        default=False,
        description="Equivale ao argumento --draw, salvando imagens com bounding boxes.",
    )


class AnnotatorResponse(BaseModel):
    comando: list[str]
    diretorio: str
    model: str
    output_dir: str
    returncode: int
    labels_resultantes: int


router = APIRouter(prefix="/api/3/annotator", tags=["Annotator"])


def resolver_caminho(caminho: str) -> Path:
    path = Path(caminho)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def contar_labels(output_dir: Path) -> int:
    if not output_dir.exists() or not output_dir.is_dir():
        return 0
    return sum(1 for path in output_dir.iterdir() if path.is_file() and path.suffix.lower() == ".txt")


def caminho_relativo(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def montar_comando(payload: AnnotatorRequest) -> tuple[list[str], Path, Path, Path]:
    diretorio = resolver_caminho(payload.diretorio)
    model = resolver_caminho(payload.model)
    output_dir = resolver_caminho(payload.output_dir)

    comando = [
        str(PYTHON_EXEC),
        str(SCRIPT_PATH),
        str(diretorio),
        "--det_model",
        str(model),
    ]

    comando.extend(["--device", payload.device])
    comando.extend(["--output_dir", str(output_dir)])
    if payload.desired_class_id is not None:
        comando.extend(["--desired_class_id", str(payload.desired_class_id)])
    if payload.draw:
        comando.append("--draw")

    return comando, diretorio, model, output_dir


def executar_anotador(payload: AnnotatorRequest) -> AnnotatorResponse:
    comando, diretorio, model, output_dir = montar_comando(payload)

    if not diretorio.exists():
        raise HTTPException(status_code=400, detail=f"Diretorio de imagens nao encontrado: {diretorio}")
    if not model.exists():
        raise HTTPException(status_code=400, detail=f"Modelo nao encontrado: {model}")

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

    response = AnnotatorResponse(
        comando=comando,
        diretorio=caminho_relativo(diretorio),
        model=caminho_relativo(model),
        output_dir=caminho_relativo(output_dir),
        returncode=returncode,
        labels_resultantes=contar_labels(output_dir),
    )

    if returncode != 0:
        raise HTTPException(status_code=500, detail=response.model_dump())

    return response


@router.post("/", response_model=AnnotatorResponse)
async def anotar(payload: AnnotatorRequest) -> AnnotatorResponse:
    return await run_in_threadpool(executar_anotador, payload)
