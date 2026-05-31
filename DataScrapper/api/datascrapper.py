from __future__ import annotations

import re
import os
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool


REPO_ROOT = Path(__file__).resolve().parents[2]
LISTAS_TERMOS_DIR = REPO_ROOT / "DataScrapper" / "listas_termos"
IMAGES_DIR = REPO_ROOT / "DataScrapper" / "images"
AUTO_ANNOTATE_LABELS_DIR = REPO_ROOT / "DataScrapper" / "images_auto_annotate_labels"
SCRIPT_PATH = REPO_ROOT / "coleta_e_limpeza.sh"
AUGMENT_TONALIDADES_SCRIPT_PATH = REPO_ROOT / "DataScrapper" / "augment_tonalidades.py"


class ColetaLimpezaRequest(BaseModel):
    nome_lista: str = Field(
        default="api_termos",
        description="Nome do arquivo .txt temporario criado em DataScrapper/listas_termos, sem extensao.",
        examples=["Dinheiro"],
    )
    termo_busca: str = Field(
        ...,
        description="Conteudo que substitui o argumento shell termo_busca. Informe os termos separados por virgula.",
        examples=["cedula de 20 reais, nota de 50 reais, dinheiro brasileiro"],
        json_schema_extra={"format": "textarea"},
    )
    limite: int = Field(default=80, ge=1, description="Limite de imagens por termo.")
    min_larg: int = Field(default=200, ge=1, description="Largura minima aceita.")
    min_alt: int = Field(default=200, ge=1, description="Altura minima aceita.")
    max_larg: int = Field(default=1280, ge=1, description="Largura maxima aceita.")
    max_alt: int = Field(default=720, ge=1, description="Altura maxima aceita.")
    limpeza: bool = Field(
        default=True,
        description="Se false, pula a etapa de limpeza do dataset.",
    )
    limpeza_visual: bool = Field(
        default=True,
        description="Equivale ao argumento --limpeza_visual do shell.",
    )
    anonimo: bool = Field(
        default=False,
        description="Se true, executa o ChromeDriver em modo anonimo.",
    )

    @field_validator("nome_lista")
    @classmethod
    def validar_nome_lista(cls, value: str) -> str:
        value = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
            raise ValueError("Use apenas letras, numeros, hifen e underline.")
        return value

    @field_validator("termo_busca")
    @classmethod
    def validar_termo_busca(cls, value: str) -> str:
        termos = [termo.strip() for termo in re.split(r"[,\n]+", value) if termo.strip()]
        if not termos:
            raise ValueError("Informe pelo menos um termo de busca.")
        return "\n".join(termos) + "\n"

    @field_validator("max_larg")
    @classmethod
    def validar_largura_maxima(cls, value: int, info) -> int:
        min_larg = info.data.get("min_larg")
        if min_larg is not None and value < min_larg:
            raise ValueError("max_larg deve ser maior ou igual a min_larg.")
        return value

    @field_validator("max_alt")
    @classmethod
    def validar_altura_maxima(cls, value: int, info) -> int:
        min_alt = info.data.get("min_alt")
        if min_alt is not None and value < min_alt:
            raise ValueError("max_alt deve ser maior ou igual a min_alt.")
        return value


class ColetaLimpezaResponse(BaseModel):
    comando: list[str]
    arquivo_termos: str
    images_dir: str
    auto_annotate_labels_dir: str
    returncode: int
    imagens_resultantes: int


class AugmentTonalidadesRequest(BaseModel):
    nome_pasta: str = Field(
        default="",
        description="Nome da pasta em DataScrapper/images_auto_annotate_labels. Se vazio, usa a data de hoje.",
        examples=["2026-05-30"],
    )

    @field_validator("nome_pasta")
    @classmethod
    def validar_nome_pasta(cls, value: str) -> str:
        value = value.strip()
        if value and not re.fullmatch(r"[A-Za-z0-9_-]+", value):
            raise ValueError("Use apenas letras, numeros, hifen e underline.")
        return value


class AugmentTonalidadesResponse(BaseModel):
    comando: list[str]
    nome_pasta: str
    input_dir: str
    output_dir: str
    returncode: int
    imagens_resultantes: int


router = APIRouter(prefix="/api/1/datascrapper", tags=["DataScrapper"])


def contar_imagens() -> int:
    return contar_imagens_em(IMAGES_DIR)


def contar_imagens_em(images_dir: Path) -> int:
    if not images_dir.exists():
        return 0

    extensoes = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".avif"}
    return sum(1 for path in images_dir.iterdir() if path.is_file() and path.suffix.lower() in extensoes)


def criar_diretorio_com_permissao(caminho: Path) -> Path:
    caminho.mkdir(parents=True, exist_ok=True, mode=0o777)
    caminho.chmod(0o777)
    return caminho


def criar_dirs_do_dia() -> tuple[Path, Path]:
    hoje = obter_nome_pasta_hoje()
    images_dir = IMAGES_DIR / hoje
    labels_dir = AUTO_ANNOTATE_LABELS_DIR / hoje
    criar_diretorio_com_permissao(images_dir)
    criar_diretorio_com_permissao(labels_dir)
    return images_dir, labels_dir


def obter_nome_pasta_hoje() -> str:
    return datetime.now(timezone(timedelta(hours=-3))).date().isoformat()


def executar_fluxo(payload: ColetaLimpezaRequest) -> ColetaLimpezaResponse:
    LISTAS_TERMOS_DIR.mkdir(parents=True, exist_ok=True)
    images_dir, labels_dir = criar_dirs_do_dia()

    termos_path = LISTAS_TERMOS_DIR / f"{payload.nome_lista}.txt"
    termos_path.write_text(payload.termo_busca, encoding="utf-8")

    comando = [
        str(SCRIPT_PATH),
        payload.nome_lista,
        str(payload.limite),
        str(payload.min_larg),
        str(payload.min_alt),
        str(payload.max_larg),
        str(payload.max_alt),
    ]
    if not payload.limpeza:
        comando.append("--sem_limpeza")
    if payload.limpeza_visual:
        comando.append("--limpeza_visual")
    if payload.anonimo:
        comando.append("--anonimo")

    env = {
        **os.environ,
        "DATASCRAPPER_IMAGES_DIR": str(images_dir),
    }

    processo = subprocess.Popen(
        comando,
        cwd=REPO_ROOT,
        env=env,
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

    def capturar_stderr() -> None:
        if processo.stderr is None:
            return
        for linha in processo.stderr:
            sys.stderr.write(linha)
            sys.stderr.flush()

    stdout_thread = threading.Thread(target=encaminhar_stdout)
    stderr_thread = threading.Thread(target=capturar_stderr)
    stdout_thread.start()
    stderr_thread.start()

    returncode = processo.wait()
    stdout_thread.join()
    stderr_thread.join()

    response = ColetaLimpezaResponse(
        comando=comando,
        arquivo_termos=str(termos_path.relative_to(REPO_ROOT)),
        images_dir=str(images_dir.relative_to(REPO_ROOT)),
        auto_annotate_labels_dir=str(labels_dir.relative_to(REPO_ROOT)),
        returncode=returncode,
        imagens_resultantes=contar_imagens_em(images_dir),
    )

    if returncode != 0:
        raise HTTPException(status_code=500, detail=response.model_dump())

    return response


def executar_augment_tonalidades(payload: AugmentTonalidadesRequest) -> AugmentTonalidadesResponse:
    nome_pasta = payload.nome_pasta or obter_nome_pasta_hoje()
    input_dir = AUTO_ANNOTATE_LABELS_DIR / nome_pasta
    output_dir = AUTO_ANNOTATE_LABELS_DIR / f"{nome_pasta}_aug"

    comando = [
        sys.executable,
        str(AUGMENT_TONALIDADES_SCRIPT_PATH),
        payload.nome_pasta,
    ]

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

    def capturar_stderr() -> None:
        if processo.stderr is None:
            return
        for linha in processo.stderr:
            sys.stderr.write(linha)
            sys.stderr.flush()

    stdout_thread = threading.Thread(target=encaminhar_stdout)
    stderr_thread = threading.Thread(target=capturar_stderr)
    stdout_thread.start()
    stderr_thread.start()

    returncode = processo.wait()
    stdout_thread.join()
    stderr_thread.join()

    response = AugmentTonalidadesResponse(
        comando=comando,
        nome_pasta=nome_pasta,
        input_dir=str(input_dir.relative_to(REPO_ROOT)),
        output_dir=str(output_dir.relative_to(REPO_ROOT)),
        returncode=returncode,
        imagens_resultantes=contar_imagens_em(output_dir),
    )

    if returncode != 0:
        raise HTTPException(status_code=500, detail=response.model_dump())

    return response


@router.post("/coleta-e-limpeza", response_model=ColetaLimpezaResponse)
async def coleta_e_limpeza(payload: ColetaLimpezaRequest) -> ColetaLimpezaResponse:
    return await run_in_threadpool(executar_fluxo, payload)


@router.post(
    "/augment-tonalidades",
    response_model=AugmentTonalidadesResponse,
    description=(
        "Aplica augmentations de tonalidade nas imagens e labels YOLO. "
        "Use este endpoint depois de concluir a anotacao YOLO em http://localhost:3000."
    ),
)
async def augment_tonalidades(payload: AugmentTonalidadesRequest) -> AugmentTonalidadesResponse:
    return await run_in_threadpool(executar_augment_tonalidades, payload)
