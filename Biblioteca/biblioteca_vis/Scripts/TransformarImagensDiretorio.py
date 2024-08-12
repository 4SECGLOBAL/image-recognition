##
##
##      Script para trocar as imagens de um padrão para outro
##       em um diretorio
##

import os, argparse, shutil
from progress.bar import Bar
from biblioteca_vis.Utils import ManuseioDiretorio as grl
from biblioteca_vis.Utils import Geral as grl1
from PIL import Image

##  PARTE DO MAIN
#Função principal
def TransformaTipoImagens(path_imgs, ALTURA_FIXA = 480):
    
    #Gera uma lista com o path das imagens somente com as extensões da lista_extensões
    lista_extensoes = ['png','jpg','jpeg']
    lista_dir_imgs = grl.lerArquivosDiretorio(                  path_imgs,
                                                                REMOVER_PONTO_EXTENSAO=False,
                                                                MANTER_PATH_COMPLETO=True,
                                                                PASSAR_EXTENSOES_ESPECIFICAS=lista_extensoes)

    bar = Bar('Transformando', fill='#', max = (len(lista_dir_imgs)), suffix='%(percent)d%%')    
    #
    for imagem_path in lista_dir_imgs:
        imagem , novo_nome = grl1.transformarTipoImagem(imagem_path)
        imagem = grl1.redimensionarImagem(imagem, ALTURA=ALTURA_FIXA)
        save_path = os.path.join(os.path.dirname(imagem_path), novo_nome)
        imagem.save(save_path, "JPEG")
        imagem.close()
        if save_path != imagem_path:
            os.remove(imagem_path)
        bar.next()
    bar.finish()
    


    