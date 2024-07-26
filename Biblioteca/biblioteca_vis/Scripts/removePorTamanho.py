##
##
##      Script para deletar imagens baseados no tamanho delas
##
##


from PIL import Image
import os
from progress.bar import Bar


def RemoverImagensPequenas(path_pasta, LARG_MIN = 10, ALT_MIN = 10):
    
    # Lista todos os arquivos no diretório
    files = os.listdir(path_pasta)
    bar = Bar('Deletando', fill='@', suffix='%(percent)d%%', max=len(os.listdir(path_pasta)))

    for file in files:
        bar.next()
        file_path = os.path.join(path_pasta, file)
        try:
            # Abre a imagem
            img = Image.open(file_path)

            # Obtém as dimensões da imagem
            width, height = img.size

            # Verifica se as dimensões são menores que os valores mínimos
            if width < LARG_MIN or height < ALT_MIN:
                # Deleta o arquivo se as dimensões forem muito pequenas
                os.remove(file_path)

        except Exception as e:
            print(f"Erro : {file}: {e}")
    bar.finish()
