##
##
##      Script para trocar o index de um Bounding Box
##
##

import os, argparse
from Utils.Geral import *
from progress.bar import Bar

##  PARTE DO MAIN
def TrocaIndex(Path, IndiceParaTrocar, IndiceNovo):

    lista_de_labels = Utils.Geral.ler_labels_para_classe(Path)

    bar = Bar('Mudando Indices: ', fill='#', max = (len(lista_de_labels)), suffix='%(percent)d%%') 
    for label in lista_de_labels:
        for BB in label.lista_de_BBs:
            if BB[0] == IndiceParaTrocar:
                BB[0] = IndiceNovo
        PathSave = os.path.join(Path, (label.nome + ".txt"))
        bar.next()
        Utils.Geral.escrever_lista_BBs_para_txt(PathSave, label.lista_de_BBs)
    bar.finish()
    return
    

if __name__ == "__main__":
    ##  PARSER
    ap = argparse.ArgumentParser(description='Processa uma pasta de labels e troca um valor de index por outro')
    ap.add_argument("-p", "--Path", required=False,default=' ',
        help="Caminho da pasta em que os labels se encontram")
    ap.add_argument("-it", "--IndiceTrocar", required=False,default=' ',
        help="Valor do Indice que será trocado")
    ap.add_argument("-in", "--IndiceNovo", required=False,default=' ',
        help="Valor do Indice novo")
    args = ap.parse_args()

    # Checa se não conter parser para adicionar manualmente
    _cwd = os.getcwd()
    if args.Path == ' ':
        path_pasta = input("Qual a pasta a ser trabalhada?\n")
        _path_pasta = os.path.join(_cwd, path_pasta)
    else:
        _path_pasta = args.Path
    
    if args.IndiceTrocar == ' ':
        _IndiceTrocar = int(input("Qual o Indice que será trocado?\n"))
    else:
        _IndiceTrocar = int(args.IndiceTrocar)
    
    if args.IndiceNovo == ' ':
        _IndiceNovo = int(input("Qual o Indice novo?\n"))
    else:
        _IndiceNovo = int(args.IndiceNovo)

    TrocaIndex(_path_pasta, _IndiceTrocar, _IndiceNovo)