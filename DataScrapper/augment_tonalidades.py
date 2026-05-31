import argparse
import cv2
import numpy as np
import shutil
from pathlib import Path
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="Aplica augmentations de tonalidade em imagens e labels YOLO.")
    parser.add_argument(
        "nome_pasta",
        nargs="?",
        default="",
        help="Nome da pasta em images_auto_annotate_labels. Se vazio, usa a data de hoje.",
    )
    return parser.parse_args()


def resolver_nome_pasta(nome_pasta: str) -> str:
    nome_pasta = nome_pasta.strip()
    if nome_pasta:
        return nome_pasta
    return datetime.now().strftime("%Y-%m-%d")


EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def escala_cinza(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def amarelado(img):
    overlay = np.full_like(img, (0, 40, 80))
    return cv2.addWeighted(img, 0.75, overlay, 0.25, 0)


def azulado(img):
    overlay = np.full_like(img, (80, 30, 0))
    return cv2.addWeighted(img, 0.75, overlay, 0.25, 0)


def infravermelho_simulado(img):
    b, g, r = cv2.split(img)
    ir = cv2.merge([
        g,
        b,
        cv2.addWeighted(r, 1.5, g, 0.5, 0)
    ])
    return np.clip(ir, 0, 255).astype(np.uint8)


def mais_claro(img):
    return cv2.convertScaleAbs(img, alpha=1.15, beta=25)


# def mais_escuro(img):
#     return cv2.convertScaleAbs(img, alpha=0.85, beta=-25)


# def contraste_alto(img):
#     return cv2.convertScaleAbs(img, alpha=1.35, beta=0)


def cftv_noite(img):
    # reduz luz e contraste, simula câmera noturna/CFTV
    escura = cv2.convertScaleAbs(img, alpha=0.55, beta=-35)

    # converte para tons esverdeados/cinzentos
    gray = cv2.cvtColor(escura, cv2.COLOR_BGR2GRAY)
    gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    overlay = np.full_like(gray_bgr, (25, 55, 25))  # BGR esverdeado
    cftv = cv2.addWeighted(gray_bgr, 0.80, overlay, 0.20, 0)

    # ruído leve de câmera
    ruido = np.random.normal(0, 12, cftv.shape).astype(np.int16)
    cftv = np.clip(cftv.astype(np.int16) + ruido, 0, 255).astype(np.uint8)

    return cftv

def mais_escuro(img):
    # levemente escuro
    return cv2.convertScaleAbs(img, alpha=0.92, beta=-10)


def muito_escuro(img):
    # ambiente interno / sombra
    return cv2.convertScaleAbs(img, alpha=0.6, beta=-50)


def contraste_alto(img):
    # aumenta contraste
    return cv2.convertScaleAbs(img, alpha=1.25, beta=0)


def contraste_baixo(img):
    # reduz contraste
    return cv2.convertScaleAbs(img, alpha=0.85, beta=10)

def desfocado(img):
    return cv2.GaussianBlur(img, (5, 5), 0)

def compressao_jpeg(img):
    _, enc = cv2.imencode(
        ".jpg",
        img,
        [cv2.IMWRITE_JPEG_QUALITY, 35]
    )
    return cv2.imdecode(enc, cv2.IMREAD_COLOR)

TRANSFORMACOES = {
    "cinza": escala_cinza,
    "amarelado": amarelado,
    "azulado": azulado,
    "infravermelho": infravermelho_simulado,
    "claro": mais_claro,
    "escuro": mais_escuro,
    "muito_escuro": muito_escuro,
    "contraste_alto": contraste_alto,
    "contraste_baixo": contraste_baixo,
    #"contraste": contraste_alto,
    "desfocado": desfocado,
    "compressao_jpeg": compressao_jpeg,
    "cftv_noite": cftv_noite,
}


def copiar_label(label_origem: Path, label_destino: Path):
    if label_origem.exists():
        shutil.copy(label_origem, label_destino)
    else:
        print(f"⚠️ Label não encontrado: {label_origem}")


def processar(nome_pasta: str):
    input_images_dir = Path(f"DataScrapper/images_auto_annotate_labels/{nome_pasta}")
    input_labels_dir = Path(f"DataScrapper/images_auto_annotate_labels/{nome_pasta}")
    output_images_dir = Path(f"DataScrapper/images_auto_annotate_labels/{nome_pasta}_aug")
    output_labels_dir = Path(f"DataScrapper/images_auto_annotate_labels/{nome_pasta}_aug")

    output_images_dir.mkdir(parents=True, exist_ok=True)
    output_labels_dir.mkdir(parents=True, exist_ok=True)

    imagens = [
        p for p in input_images_dir.rglob("*")
        if p.suffix.lower() in EXTENSOES
    ]

    print(f"Encontradas {len(imagens)} imagens.")

    for img_path in imagens:
        img = cv2.imread(str(img_path))

        if img is None:
            print(f"⚠️ Erro ao abrir imagem: {img_path}")
            continue

        stem = img_path.stem
        suffix = img_path.suffix

        label_original = input_labels_dir / f"{stem}.txt"

        # salva imagem original no dataset aumentado
        imagem_original_destino = output_images_dir / img_path.name
        label_original_destino = output_labels_dir / f"{stem}.txt"

        cv2.imwrite(str(imagem_original_destino), img)
        copiar_label(label_original, label_original_destino)

        # salva imagens transformadas + labels correspondentes
        for nome_transformacao, funcao in TRANSFORMACOES.items():
            nova_img = funcao(img)

            novo_stem = f"{stem}_{nome_transformacao}"
            nova_imagem_destino = output_images_dir / f"{novo_stem}{suffix}"
            novo_label_destino = output_labels_dir / f"{novo_stem}.txt"

            cv2.imwrite(str(nova_imagem_destino), nova_img)

            # como só muda tonalidade, o label YOLO é igual
            copiar_label(label_original, novo_label_destino)

    print("✅ Augmentation concluído com imagens e labels YOLO.")


if __name__ == "__main__":
    args = parse_args()
    processar(resolver_nome_pasta(args.nome_pasta))
