##
##
##      Script para deletar duplicatas usando o metodo HashD
##
##

import cv2,os,argparse
from progress.bar import Bar

def hashd(img, hash_size = 9):
    # :redimencionar a imagem para o tamanho que iremos trabalhar
    rez = cv2.resize(img, (hash_size+1, hash_size))
    # :computa a diferença
    dif = rez[:,1:]>rez[:,:-1]

    # converte da lista de verdadeiros e falsos em bits
    # (v = 1; f = 0) retornando um int
    return sum([2 ** i for (i, v) in enumerate(dif.flatten()) if v])




def RemoverDuplicata(_path_pasta, RANGE_DE_DIMENSAO_PARA_HASH = range(5,7)):
    contador = 0
    #Passa o hash com redimencionamento de imagen entre 4-7 pra abranger maior numero de imagens copiadas
    for sizeHASH in RANGE_DE_DIMENSAO_PARA_HASH:
        bar = Bar('Processando Hashes '+str(sizeHASH), fill='@', suffix='%(percent)d%%', max=len(os.listdir(_path_pasta)))
        haystack = {}
        for x in os.listdir(_path_pasta):
            _path_img = os.path.join(_path_pasta, x)
            if os.path.isfile(_path_img):
                image = cv2.imread(_path_img)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                xHash = hashd(image, hash_size=sizeHASH)
                
                l = haystack.get(xHash, [])
                l.append(_path_img)
                haystack[xHash] = l
            bar.next()
        bar.finish()
        for key in haystack:
            x = haystack.get(key, [])
            if len(x) > 1:
                print("Removed:")
                for i in x[1:]:
                    print(" {}".format(i))
                    os.remove(i)
                    contador += 1

        print("Imagens repetidas: {}".format(contador))
            
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
    
    RemoverDuplicata(_path_pasta)
