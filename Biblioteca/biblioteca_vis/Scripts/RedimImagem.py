##
##
##      Script para redimensionar todas as imagens de uma pasta para uma
##          altura padrão
##

import os, argparse, shutil
from progress.bar import Bar
import Utils.Geral
from PIL import Image

##  PARTE DO MAIN
#Função principal
def redimensionarImagens(path_imgs, ALTURA_FIXA=640, FORMATO_FINAL = 'JPEG'):
    #Gera uma lista com o path das imagens
    lista_extensoes = ['png','jpg','jpeg']
    lista_dir_imgs = Utils.Geral.ler_arquivos_de_um_diretorio(path_imgs,
                                                                REMOVER_PONTO_EXTENSAO=False,
                                                                MANTER_PATH_COMPLETO=True,
                                                                PASSAR_EXTENSOES_ESPECIFICAS=lista_extensoes)

    bar = Bar('redimensionando', fill='#', max = (len(lista_dir_imgs)), suffix='%(percent)d%%')    
    #Compara os arquivos no dir com os nomes de arquivos de refetencia
    for imagem_path in lista_dir_imgs:
        imagem , novo_nome = Utils.Geral.transformar_tipo_imagem(imagem_path,TRANSFORMAR_EM_TIPO=FORMATO_FINAL)
        imagem = Utils.Geral.redimensionar_imagem(imagem, ALTURA=ALTURA_FIXA)
        save_path = os.path.join(os.path.dirname(imagem_path), novo_nome)
        imagem.save(save_path, FORMATO_FINAL)
        imagem.close()
        if save_path != imagem_path:
            os.remove(imagem_path)
        bar.next()
    bar.finish()
    


    
    

if __name__ == "__main__":
    ##  PARSER
    ap = argparse.ArgumentParser(description="redimensiona todas as imagens de uma pasta para uma altura padrão")
    ap.add_argument("-p", "--Path", required=False,default=' ',
        help="Caminho da pasta em que as imagens estão localizadas")
    ap.add_argument("-a", "--AlturaFixa", required=False,default=' ',
        help="Altura padrão a ser adotada por todas as imagens; Padrão = 640")
    args = ap.parse_args()

    # Checa se não conter parser para adicionar manualmente
    _cwd = os.getcwd()
    if args.Path == ' ':
        Path = input("Qual a pasta em que as imagens estão localizadas?\n")
        _Path = os.path.join(_cwd, Path)
    else:
        _Path = args.Path
    
    if args.AlturaFixa == ' ':
        AlturaFixa = int(input("Qual a altura padrão a ser adotada por todas as imagens?\n"))
    else:
        AlturaFixa = int(args.Path)

    redimensionarImagens(_Path, ALTURA_FIXA=AlturaFixa)