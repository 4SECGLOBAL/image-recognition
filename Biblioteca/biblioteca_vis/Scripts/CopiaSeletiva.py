##
##
##      Script para Copiar somente arquivos de uma pasta quando uma segunda pasta
##          de refetencia tambem contem tal arquivo
##

import os, argparse, shutil
from progress.bar import Bar
import Utils.Geral

##  PARTE DO MAIN
#Função principal
def CopiaSeletivaf(pathSave, pathRef, pathCopia, MOVER = False):
    #Gera lista com o nomes dos arquivos sem a extensão (i.e ".txt")
    lista_dir_ref = Utils.Geral.ler_arquivos_de_um_diretorio(pathRef)
     
    #Cria a pasta para salvar caso não exista
    Utils.Geral.criar_diretorio(pathSave)

    bar = Bar('Movendo: ', fill='#', max = (len(lista_dir_ref)), suffix='%(percent)d%%')    
    #Compara os arquivos no dir com os nomes de arquivos de refetencia
    for arquivo in os.listdir(pathCopia):
        if arquivo.rsplit('.',1)[0] in lista_dir_ref:
            if MOVER == True:
                shutil.move(os.path.join(pathCopia, arquivo), os.path.join(pathSave, arquivo)) #Move para a pasta final
                bar.next()
            else:
                shutil.copy(os.path.join(pathCopia, arquivo), pathSave) #Copia para a pasta final
                bar.next()
    bar.finish()
    


    
    

if __name__ == "__main__":
    ##  PARSER
    ap = argparse.ArgumentParser(description="Copia somente arquivos de uma pasta quando um com o mesmo nome está contido uma segunda pasta de referencia")
    ap.add_argument("-ps", "--PathSave", required=False,default=' ',
        help="Caminho da pasta em que os arquivos serão copiados")
    ap.add_argument("-pr", "--PathReferencia", required=False,default=' ',
        help="Caminho da pasta de referencia")
    ap.add_argument("-pc", "--PastaParaCopiar", required=False,default=' ',
        help="Caminho da pasta para copiar")
    args = ap.parse_args()

    # Checa se não conter parser para adicionar manualmente
    _cwd = os.getcwd()
    if args.PathSave == ' ':
        PathSave = input("Qual a pasta em que serão salvos os arquivos?\n")
        _PathSave = os.path.join(_cwd, PathSave)
    else:
        _PathSave = args.PathSave
    
    if args.PathReferencia == ' ':
        PathReferencia = input("Qual a pasta de referencia?\n")
        _PathReferencia = os.path.join(_cwd, PathReferencia)
    else:
        _PathReferencia = args.PathReferencia
    
    if args.PastaParaCopiar == ' ':
        pastaParaCopiar = input("Qual a pasta aonde os arquivos que serão copiados se encontram?\n")
        _pastaParaCopiar = os.path.join(_cwd, pastaParaCopiar)
    else:
        _pastaParaCopiar = args.PastaParaCopiar

    CopiaSeletivaf(_PathSave, _PathReferencia, _pastaParaCopiar)