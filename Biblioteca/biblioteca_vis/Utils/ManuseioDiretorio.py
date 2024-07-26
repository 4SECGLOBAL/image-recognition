import os, shutil
from progress.bar import Bar
from PIL import Image
from biblioteca_vis.Utils.Classes import *

"""
            FUNÇÕES DE DIRETORIO
            -Principal função dessa seção é gerar funções de manuseamento de diretorios
            seja para criar, copiar ou verificar diretorios, além de carregar possiveis
            dados
"""


## FUNÇÃO PARA CRIAR DIRETORIO
# -Recebe um path para um diretorio e tem a opção de adicionar sufixo se a pasta já exisir
# e também de levantar um erro no caso da existencia
def criarDiretorio(dir, ADD_SUFIXO_SE_EXISTIR = False,RETORNA_ERRO_SE_EXISTIR = False):
    dir_final = dir
    contador = 0
    # Caso base em que a pasta não existe
    if not os.path.exists(dir_final):
        os.mkdir(dir_final)
        return dir_final
    # Usado caso a pasta exista e for de interesse levantar um erro sobre a existencia da mesma
    elif RETORNA_ERRO_SE_EXISTIR == True:
        raise Exception("A Pasta {} já existe no diretorio: \n {}".format(os.path.basename(dir_final), dir_final))
    # Caso em que a pasta exista, mas é de interesse criar uma nova com um sufixo para diferenciar
    elif ADD_SUFIXO_SE_EXISTIR == True:
        while True:
            contador = contador + 1
            dir_final = dir + "_" + str(contador)
            if not os.path.exists(dir_final):
                os.mkdir(dir_final)
                return dir_final
    # Caso final, caso já exista e nao queira fazer nada a respeito, só retorna o diretorio da pasta
    else:
        return dir_final
# -Retorna o diretorio criado

##  FUNÇÃO PARA LER OS ARQUIVOS DE UM DIRETORIO
# -Recebe um path de diretorio e retorna todo o conteudo dele em uma lista
# Tem opções para escolher se tem a extensão no nome do arquivo, quais extensões são selecionadas
# ou mesmo a opção de manter todo o path para o arquivo ao inves de somente o nome
def lerArquivosDiretorio(dir, REMOVER_PONTO_EXTENSAO = True, PASSAR_EXTENSOES_ESPECIFICAS = [], MANTER_PATH_COMPLETO = False):
    bar = Bar('Lendo Dir: ', fill='#', max = len(os.listdir(dir)), suffix='%(percent)d%%')    
    lista_de_arquivos = []
    for arquivo in os.listdir(dir):
        if (arquivo.rsplit('.',1)[1] in PASSAR_EXTENSOES_ESPECIFICAS) or (len(PASSAR_EXTENSOES_ESPECIFICAS) == 0):
            if REMOVER_PONTO_EXTENSAO:
                arquivo = arquivo.rsplit('.',1)[0]
            if MANTER_PATH_COMPLETO:
                arquivo = os.path.join(dir, arquivo)
            lista_de_arquivos.append(arquivo)
            bar.next()
    bar.finish()
    return lista_de_arquivos
# -Retorna uma lista com todos os arquivos


