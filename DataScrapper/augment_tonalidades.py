import argparse
import cv2
import hashlib
import json
import numpy as np
import shutil
from pathlib import Path
from datetime import datetime
from time import perf_counter


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
SEM_FUNDO_NOME = "sem_fundo"
ORIGINAL_NOME = "original"
MAX_NOME_ARQUIVO_BYTES = 255
MAX_SUFFIX_BYTES = max(len(extensao.encode("utf-8")) for extensao in EXTENSOES | {".txt"})


def nome_arquivo_augmentado(stem: str, transformacao: str) -> str:
    sufixo_augmentation = f"_{transformacao}__aug"
    nome_completo = f"{stem}{sufixo_augmentation}"
    limite_stem = MAX_NOME_ARQUIVO_BYTES - MAX_SUFFIX_BYTES

    if len(nome_completo.encode("utf-8")) <= limite_stem:
        return nome_completo

    hash_nome = hashlib.sha256(stem.encode("utf-8")).hexdigest()[:12]
    sufixo_seguro = f"_{hash_nome}{sufixo_augmentation}"
    limite_prefixo = limite_stem - len(sufixo_seguro.encode("utf-8"))
    prefixo = stem.encode("utf-8")[:limite_prefixo].decode("utf-8", errors="ignore")
    return f"{prefixo}{sufixo_seguro}"


def escala_cinza(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def amarelado(img):
    overlay = np.full_like(img, (0, 40, 80))
    return cv2.addWeighted(img, 0.75, overlay, 0.25, 0)


def azulado(img):
    overlay = np.full_like(img, (80, 30, 0))
    return cv2.addWeighted(img, 0.75, overlay, 0.25, 0)


def esverdeada(img):
    overlay = np.full_like(img, (30, 80, 30))
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
    return ajustar_intensidade(img, alpha=1.15, beta=25)


def ajustar_intensidade(img, alpha: float, beta: float):
    """Ajusta brilho/contraste sem refletir valores negativos."""
    ajustada = img.astype(np.float32) * alpha + beta
    return np.clip(ajustada, 0, 255).astype(np.uint8)


# def mais_escuro(img):
#     return cv2.convertScaleAbs(img, alpha=0.85, beta=-25)


# def contraste_alto(img):
#     return cv2.convertScaleAbs(img, alpha=1.35, beta=0)


def cftv_noite(img):
    # reduz luz e contraste, simula câmera noturna/CFTV
    escura = ajustar_intensidade(img, alpha=0.55, beta=-35)

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
    return ajustar_intensidade(img, alpha=0.92, beta=-10)


def muito_escuro(img):
    # ambiente interno / sombra
    return ajustar_intensidade(img, alpha=0.6, beta=-50)


def contraste_alto(img):
    # aumenta contraste
    return ajustar_intensidade(img, alpha=1.25, beta=0)


def contraste_baixo(img):
    # reduz contraste
    return ajustar_intensidade(img, alpha=0.85, beta=10)

def desfocado(img):
    return cv2.GaussianBlur(img, (5, 5), 0)

def compressao_jpeg(img):
    _, enc = cv2.imencode(
        ".jpg",
        img,
        [cv2.IMWRITE_JPEG_QUALITY, 35]
    )
    return cv2.imdecode(enc, cv2.IMREAD_COLOR)


def fundo_ja_branco(img):
    altura, largura = img.shape[:2]
    borda = max(4, min(30, int(min(altura, largura) * 0.04)))

    amostras = np.concatenate([
        img[:borda, :, :].reshape(-1, 3),
        img[-borda:, :, :].reshape(-1, 3),
        img[:, :borda, :].reshape(-1, 3),
        img[:, -borda:, :].reshape(-1, 3),
    ])

    pixels_brancos = np.all(amostras >= 245, axis=1)
    return np.mean(pixels_brancos) >= 0.85


def remover_background(img):
    if fundo_ja_branco(img):
        return None

    altura, largura = img.shape[:2]
    margem_x = max(1, int(largura * 0.05))
    margem_y = max(1, int(altura * 0.05))
    rect = (
        margem_x,
        margem_y,
        max(1, largura - (2 * margem_x)),
        max(1, altura - (2 * margem_y)),
    )

    mask = np.zeros((altura, largura), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        return img

    foreground_mask = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD),
        255,
        0,
    ).astype(np.uint8)

    area_foreground = np.mean(foreground_mask > 0)
    if area_foreground < 0.02 or area_foreground > 0.98:
        return img

    kernel = np.ones((3, 3), np.uint8)
    foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel)
    foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_CLOSE, kernel)
    foreground_mask = cv2.GaussianBlur(foreground_mask, (5, 5), 0)

    alpha = foreground_mask.astype(np.float32) / 255.0
    alpha = alpha[:, :, None]
    fundo_branco = np.full_like(img, 255)
    return (img.astype(np.float32) * alpha + fundo_branco.astype(np.float32) * (1 - alpha)).astype(np.uint8)


def rotacionada_90(img):
    return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)


def rotacionada_180(img):
    return cv2.rotate(img, cv2.ROTATE_180)


def rotacionada_270(img):
    return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)


def espelhada(img):
    return cv2.flip(img, 1)


TRANSFORMACOES = {
    "cinza": escala_cinza,
    "amarelado": amarelado,
    "azulado": azulado,
    "esverdeada": esverdeada,
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

TRANSFORMACOES_GEOMETRICAS = {
    "rot90": rotacionada_90,
    "rot180": rotacionada_180,
    "rot270": rotacionada_270,
    "espelhada": espelhada,
}


def limitar_normalizado(valor: float) -> float:
    return min(1.0, max(0.0, valor))


def transformar_bbox_yolo(tipo_transformacao: str, x: float, y: float, largura: float, altura: float):
    if tipo_transformacao == "rot90":
        return 1 - y, x, altura, largura
    if tipo_transformacao == "rot180":
        return 1 - x, 1 - y, largura, altura
    if tipo_transformacao == "rot270":
        return y, 1 - x, altura, largura
    if tipo_transformacao == "espelhada":
        return 1 - x, y, largura, altura
    return x, y, largura, altura


def transformar_label_geometrico(label_origem: Path, label_destino: Path, tipo_transformacao: str) -> bool:
    if not label_origem.exists():
        print(f"AVISO: Label não encontrado: {label_origem}")
        return False

    linhas_transformadas = []
    for linha in label_origem.read_text(encoding="utf-8").splitlines():
        partes = linha.split()
        if len(partes) < 5:
            linhas_transformadas.append(linha)
            continue

        classe = partes[0]
        try:
            x, y, largura, altura = map(float, partes[1:5])
        except ValueError:
            linhas_transformadas.append(linha)
            continue

        novo_x, novo_y, nova_largura, nova_altura = transformar_bbox_yolo(
            tipo_transformacao,
            x,
            y,
            largura,
            altura,
        )
        bbox = [
            limitar_normalizado(novo_x),
            limitar_normalizado(novo_y),
            limitar_normalizado(nova_largura),
            limitar_normalizado(nova_altura),
        ]
        extras = partes[5:]
        linhas_transformadas.append(
            " ".join([classe, *(f"{valor:.6f}" for valor in bbox), *extras])
        )

    label_destino.write_text("\n".join(linhas_transformadas) + "\n", encoding="utf-8")
    return True


def copiar_label(label_origem: Path, label_destino: Path):
    if label_origem.exists():
        shutil.copy(label_origem, label_destino)
        return True
    else:
        print(f"AVISO: Label não encontrado: {label_origem}")
        return False


def processar_sem_fundo_em_lote(imagens, input_labels_dir, output_images_dir, output_labels_dir):
    input_labels_dir = Path(input_labels_dir)
    output_images_dir = Path(output_images_dir)
    output_labels_dir = Path(output_labels_dir)
    inicio = perf_counter()
    geradas = 0
    puladas = 0
    erros = 0
    labels_faltantes = 0

    for img_path_str in imagens:
        img_path = Path(img_path_str)
        img = cv2.imread(str(img_path))

        if img is None:
            erros += 1
            continue

        nova_img = remover_background(img)
        if nova_img is None:
            puladas += 1
            continue

        stem = img_path.stem
        suffix = img_path.suffix
        novo_stem = nome_arquivo_augmentado(stem, SEM_FUNDO_NOME)
        nova_imagem_destino = output_images_dir / f"{novo_stem}{suffix}"
        novo_label_destino = output_labels_dir / f"{novo_stem}.txt"

        if not cv2.imwrite(str(nova_imagem_destino), nova_img):
            erros += 1
            continue

        label_original = input_labels_dir / f"{stem}.txt"
        if label_original.exists():
            shutil.copy(label_original, novo_label_destino)
        else:
            labels_faltantes += 1

        geradas += 1

    return {
        "geradas": geradas,
        "puladas": puladas,
        "erros": erros,
        "labels_faltantes": labels_faltantes,
        "duracao": perf_counter() - inicio,
    }


def processar(nome_pasta: str):
    input_images_dir = Path(f"DataScrapper/images_auto_annotate_labels/{nome_pasta}")
    input_labels_dir = Path(f"DataScrapper/images_auto_annotate_labels/{nome_pasta}")
    output_images_dir = Path(f"DataScrapper/images_auto_annotate_labels/{nome_pasta}_aug")
    output_labels_dir = Path(f"DataScrapper/images_auto_annotate_labels/{nome_pasta}_aug")

    imagens_encontradas = [
        p for p in input_images_dir.rglob("*")
        if p.suffix.lower() in EXTENSOES
    ]

    if not input_images_dir.is_dir():
        raise FileNotFoundError(f"Diretório de entrada não encontrado: {input_images_dir}")
    if not imagens_encontradas:
        raise ValueError(f"Nenhuma imagem encontrada em: {input_images_dir}")

    imagens = []
    imagens_invalidas = 0
    labels_faltantes = 0
    print("\nValidando imagens e labels...")
    for img_path in imagens_encontradas:
        if cv2.imread(str(img_path)) is None:
            print(f"AVISO: Erro ao abrir imagem: {img_path}")
            imagens_invalidas += 1
            continue

        label_original = input_labels_dir / f"{img_path.stem}.txt"
        if not label_original.is_file():
            print(f"AVISO: Label não encontrado: {label_original}")
            labels_faltantes += 1
            continue

        imagens.append(img_path)

    if not imagens:
        raise ValueError("Nenhuma imagem válida com label foi encontrada para augmentation.")

    # A saída é reconstruída para não misturar artefatos de execuções anteriores.
    if output_images_dir.is_symlink():
        raise ValueError(f"O diretório de saída não pode ser um link simbólico: {output_images_dir}")
    if output_images_dir.exists():
        shutil.rmtree(output_images_dir)
    output_images_dir.mkdir(parents=True, exist_ok=True)

    total_imagens = len(imagens)
    total_transformacoes = len(TRANSFORMACOES) + len(TRANSFORMACOES_GEOMETRICAS)
    total_geradas = 0
    total_puladas = 0
    total_erros = imagens_invalidas
    inicio = perf_counter()

    print("\nIniciando augmentation de tonalidades")
    print(f"Entrada: {input_images_dir}")
    print(f"Saída: {output_images_dir}")
    print(f"Imagens encontradas: {len(imagens_encontradas)}")
    print(f"Imagens válidas com label: {total_imagens}")
    print(f"Imagens inválidas: {imagens_invalidas}")
    print(f"Labels faltantes: {labels_faltantes}")
    print(f"Transformações: {total_transformacoes}")

    print("\nCopiando imagens originais e labels...")
    originais_copiadas = 0
    for img_path in imagens:
        img = cv2.imread(str(img_path))

        if img is None:
            print(f"AVISO: Erro ao abrir imagem: {img_path}")
            total_erros += 1
            continue

        stem = img_path.stem
        label_original = input_labels_dir / f"{stem}.txt"

        # salva imagem original no dataset aumentado
        novo_stem = nome_arquivo_augmentado(stem, ORIGINAL_NOME)
        imagem_original_destino = output_images_dir / f"{novo_stem}{img_path.suffix}"
        label_original_destino = output_labels_dir / f"{novo_stem}.txt"

        if not cv2.imwrite(str(imagem_original_destino), img):
            print(f"AVISO: Erro ao salvar imagem original: {imagem_original_destino.name}")
            total_erros += 1
            continue

        if not copiar_label(label_original, label_original_destino):
            total_erros += 1
            imagem_original_destino.unlink(missing_ok=True)
            continue

        originais_copiadas += 1

    print(f"OK: Originais copiadas: {originais_copiadas}/{total_imagens}")

    # A transformação `sem_fundo` está temporariamente desativada por seu alto
    # custo de processamento e por poder remover objetos ainda anotados no YOLO.
    # Para reativá-la, executar `processar_sem_fundo_em_lote` em uma etapa própria.

    for indice_transformacao, (nome_transformacao, funcao) in enumerate(TRANSFORMACOES.items(), start=1):
        inicio_transformacao = perf_counter()
        geradas = 0
        puladas = 0
        erros = 0

        print(f"\n[{indice_transformacao}/{total_transformacoes}] Aplicando: {nome_transformacao}")

        for indice_imagem, img_path in enumerate(imagens, start=1):
            img = cv2.imread(str(img_path))

            if img is None:
                print(f"  AVISO: [{indice_imagem}/{total_imagens}] Erro ao abrir imagem: {img_path.name}")
                erros += 1
                continue

            stem = img_path.stem
            suffix = img_path.suffix
            label_original = input_labels_dir / f"{stem}.txt"

            nova_img = funcao(img)
            if nova_img is None:
                puladas += 1
                continue

            novo_stem = nome_arquivo_augmentado(stem, nome_transformacao)
            nova_imagem_destino = output_images_dir / f"{novo_stem}{suffix}"
            novo_label_destino = output_labels_dir / f"{novo_stem}.txt"

            if not cv2.imwrite(str(nova_imagem_destino), nova_img):
                print(f"  AVISO: [{indice_imagem}/{total_imagens}] Erro ao salvar imagem: {nova_imagem_destino.name}")
                erros += 1
                continue

            # como só muda tonalidade, o label YOLO é igual
            copiar_label(label_original, novo_label_destino)
            geradas += 1

        duracao_transformacao = perf_counter() - inicio_transformacao
        total_geradas += geradas
        total_puladas += puladas
        total_erros += erros

        print(
            f"OK: {nome_transformacao}: {geradas} geradas, "
            f"{puladas} puladas, {erros} erros em {duracao_transformacao:.1f}s"
        )

    inicio_geometricas = len(TRANSFORMACOES) + 1
    for offset, (nome_transformacao, funcao) in enumerate(TRANSFORMACOES_GEOMETRICAS.items()):
        indice_transformacao = inicio_geometricas + offset
        inicio_transformacao = perf_counter()
        geradas = 0
        puladas = 0
        erros = 0

        print(f"\n[{indice_transformacao}/{total_transformacoes}] Aplicando: {nome_transformacao}")

        for indice_imagem, img_path in enumerate(imagens, start=1):
            img = cv2.imread(str(img_path))

            if img is None:
                print(f"  AVISO: [{indice_imagem}/{total_imagens}] Erro ao abrir imagem: {img_path.name}")
                erros += 1
                continue

            stem = img_path.stem
            suffix = img_path.suffix
            label_original = input_labels_dir / f"{stem}.txt"
            novo_stem = nome_arquivo_augmentado(stem, nome_transformacao)
            nova_imagem_destino = output_images_dir / f"{novo_stem}{suffix}"
            novo_label_destino = output_labels_dir / f"{novo_stem}.txt"

            nova_img = funcao(img)
            if not cv2.imwrite(str(nova_imagem_destino), nova_img):
                print(f"  AVISO: [{indice_imagem}/{total_imagens}] Erro ao salvar imagem: {nova_imagem_destino.name}")
                erros += 1
                continue

            if not transformar_label_geometrico(label_original, novo_label_destino, nome_transformacao):
                puladas += 1

            geradas += 1

        duracao_transformacao = perf_counter() - inicio_transformacao
        total_geradas += geradas
        total_puladas += puladas
        total_erros += erros

        print(
            f"OK: {nome_transformacao}: {geradas} geradas, "
            f"{puladas} labels ausentes/inalterados, {erros} erros em {duracao_transformacao:.1f}s"
        )

    duracao_total = perf_counter() - inicio
    print("\nAugmentation concluído com imagens e labels YOLO.")
    print(f"Originais copiadas: {originais_copiadas}")
    print(f"Transformadas geradas: {total_geradas}")
    print(f"Transformações puladas: {total_puladas}")
    print(f"Erros: {total_erros}")
    print(f"Tempo total: {duracao_total:.1f}s")
    resumo = {
        "imagens_encontradas": len(imagens_encontradas),
        "imagens_validas": total_imagens,
        "imagens_invalidas": imagens_invalidas,
        "labels_faltantes": labels_faltantes,
        "originais_copiadas": originais_copiadas,
        "transformadas_geradas": total_geradas,
        "transformacoes_puladas": total_puladas,
        "erros": total_erros,
        "duracao_segundos": round(duracao_total, 3),
    }
    print(f"RESUMO_AUGMENTACAO={json.dumps(resumo, ensure_ascii=False)}")
    return resumo


if __name__ == "__main__":
    args = parse_args()
    processar(resolver_nome_pasta(args.nome_pasta))
