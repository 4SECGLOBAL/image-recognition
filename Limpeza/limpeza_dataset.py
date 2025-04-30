import os
import sys
import hashlib
from PIL import Image
import argparse

try:
    import imagehash
except ImportError:
    print("Por favor, instale a biblioteca 'imagehash' com: pip install ImageHash")
    sys.exit(1)


def obter_imagens(caminho_entrada):
    """Retorna lista de caminhos de imagem a partir de diretório ou .txt"""
    if os.path.isdir(caminho_entrada):
        return [
            os.path.join(caminho_entrada, f)
            for f in os.listdir(caminho_entrada)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'))
        ]
    elif os.path.isfile(caminho_entrada) and caminho_entrada.lower().endswith('.txt'):
        with open(caminho_entrada, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    else:
        raise ValueError(f"Caminho inválido: {caminho_entrada}")


def gerar_hash(img, usar_phash=False):
    """Gera hash (simples ou perceptual) da imagem"""
    try:
        if usar_phash:
            return str(imagehash.phash(img))
        else:
            return hashlib.md5(img.tobytes()).hexdigest()
    except Exception:
        return None


def tamanho_valido(img, min_w, min_h, max_w, max_h):
    """Verifica se a imagem está dentro dos limites de dimensão"""
    largura, altura = img.size
    return min_w <= largura <= max_w and min_h <= altura <= max_h


def limpar_imagens(imagens, min_w, min_h, max_w, max_h, usar_phash):
    hashes_vistos = set()
    removidas = 0
    mantidas = 0

    for caminho in imagens:
        if not os.path.exists(caminho):
            print(f"[Ignorado] Arquivo não encontrado: {caminho}")
            continue

        try:
            with Image.open(caminho) as img:
                img = img.convert('RGB')

                hash_img = gerar_hash(img, usar_phash)
                if not hash_img:
                    print(f"[Removida] Imagem corrompida: {caminho}")
                    os.remove(caminho)
                    removidas += 1
                    continue

                if hash_img in hashes_vistos:
                    print(f"[Removida] Imagem duplicada: {caminho}")
                    os.remove(caminho)
                    removidas += 1
                    continue

                if not tamanho_valido(img, min_w, min_h, max_w, max_h):
                    print(f"[Removida] Tamanho inválido {img.size}: {caminho}")
                    os.remove(caminho)
                    removidas += 1
                    continue

                hashes_vistos.add(hash_img)
                mantidas += 1
        except Exception as e:
            print(f"[Erro] {caminho}: {e}")
            try:
                os.remove(caminho)
                removidas += 1
            except:
                pass

    print(f"\n✅ Limpeza concluída. Imagens mantidas: {mantidas}, removidas: {removidas}")


def main():
    parser = argparse.ArgumentParser(description="Limpa dataset de imagens (duplicadas e fora do tamanho)")
    parser.add_argument("entrada", help="Diretório ou arquivo .txt com caminhos de imagem")
    parser.add_argument("--min_width", type=int, default=100, help="Largura mínima")
    parser.add_argument("--min_height", type=int, default=100, help="Altura mínima")
    parser.add_argument("--max_width", type=int, default=5000, help="Largura máxima")
    parser.add_argument("--max_height", type=int, default=5000, help="Altura máxima")
    parser.add_argument("--limpeza_visual", action='store_true', help="Usa hash perceptual para detectar duplicatas visuais")

    args = parser.parse_args()

    imagens = obter_imagens(args.entrada)
    limpar_imagens(imagens, args.min_width, args.min_height, args.max_width, args.max_height, args.limpeza_visual)


if __name__ == "__main__":
    main()
