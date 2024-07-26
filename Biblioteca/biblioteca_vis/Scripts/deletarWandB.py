##
##
##      Script para deletar imagens baseados se são ou não preto em brancas
##
##

from PIL import Image
import os
from progress.bar import Bar

def is_BandW(image_path):
    try:
        img = Image.open(image_path)

        img_gray = img.convert('L')
        unique_colors = set(img_gray.getdata())

        # Se houver apenas uma cor, a imagem é preto e branco
        return len(unique_colors) == 1

    except Exception as e:
        print(f"Erro = {image_path}: {e}")
        return False

def RemoverPretoEBranco(path_pasta):
    files = os.listdir(path_pasta)
    bar = Bar('Deletando', fill='@', suffix='%(percent)d%%', max=len(os.listdir(path_pasta)))

    for file in files:
        bar.next()
        file_path = os.path.join(path_pasta, file)
        if is_BandW(file_path):
            os.remove(file_path)
    bar.finish()
