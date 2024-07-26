##
##
##      Script para deletar imagens baseados no tipo de imagem
##
##

import cv2,os,argparse
from progress.bar import Bar

def RemoverPorTipo(_path_pasta):
    bar = Bar('Deletando', fill='@', suffix='%(percent)d%%', max=len(os.listdir(_path_pasta)))
    for x in [o for o in os.listdir(_path_pasta) if not (o.endswith(".jpg") or o.endswith(".png") or o.endswith(".jpeg") or o.endswith(".webp"))]:
        _path_img = os.path.join(_path_pasta, x)
        if os.path.isfile(_path_img):
            os.remove(_path_img)
        bar.next()
    bar.finish()
            
if __name__ == "__main__":
    ##  PARSER
    ap = argparse.ArgumentParser(description='Processa uma pasta de imagens e remove as duplicatas')
    ap.add_argument("-p", "--Path", required=False,default=' ',
        help="Caminho da pasta em que as imagens do dataset se encontram")
    args = ap.parse_args()

    # Checa se não conter parser para adicionar manualmente
    _cwd = os.getcwd()
    if args.Path == ' ':
        path_pasta = input("Qual a pasta a ser trabalhada?\n")
        _path_pasta = os.path.join(_cwd, path_pasta)
    else:
        _path_pasta = args.Path
    
    RemoverPorTipo(_path_pasta)
