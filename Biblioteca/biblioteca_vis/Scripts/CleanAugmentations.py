##
##
##      Script para remover augmentations de um dataset
##          
##

import os

def deletarAugmentationsf(diretorio):
    # Obtém a lista de arquivos no diretório
    arquivos = os.listdir(diretorio) 

    # Passa pelos arquivos em um diretorio
    for arquivo in arquivos:
        arquivo_path = os.path.join(diretorio, arquivo)
        if os.path.isfile(arquivo_path):
            if "AUG" in arquivo:
                os.remove(arquivo_path)
                print(f"Arquivo '{arquivo}' visto como augmentation foi deletado.")
        elif os.path.isdir(arquivo_path):
            deletarAugmentationsf(arquivo_path)
    return 0