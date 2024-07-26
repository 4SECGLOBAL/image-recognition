import os, shutil
from progress.bar import Bar
from PIL import Image
from biblioteca_vis.Utils.Classes import *



##
##          FUNÇÕES
##

## FUNÇÃO DE REDIMENCIONAMENTO DE IMAGENS
# Redimenciona a imagem mantendo o Aspect Ratio da mesma
def redimencionarImagem(imagem, ALTURA = 640):
    if(imagem.size[1] != ALTURA):
        imagem = imagem.resize((int((imagem.size[0]/imagem.size[1])*ALTURA),ALTURA))
    return imagem

## FUNÇÃO DE TRANSFORMAÇÃO DO TIPO DE IMAGENS
# Abre uma imagem e transforma a mesma em .png ou .jpg
def transformarTipoImagem(path_imagem, TRANSFORMAR_EM_TIPO = "JPEG"):
    imagem = Image.open(path_imagem)
    nome_imagem = os.path.basename(path_imagem).rsplit('.',1)[0]
    if imagem.mode != "RGB":                        # Garante que caso tenha um canal alfa no tipo png
        imagem = imagem.convert("RGB")              # a imagem volte a ser somente RGB
    if TRANSFORMAR_EM_TIPO.upper() == "JPEG" or TRANSFORMAR_EM_TIPO.upper() == "JPG":
        nome_imagem = nome_imagem + ".jpg"
    elif TRANSFORMAR_EM_TIPO.upper() == "PNG":
        nome_imagem = nome_imagem + ".png"
    else:
        raise Exception("O Formato de imagem escolhido não é suportado")
    return imagem, nome_imagem



"""
        FUNÇÕES DE DATASET
        -Essa seção é dedicada para funções de apoio para manusear o dataset

"""
def checar_se_tem_tamanho_minimo_BB_XYWH(BB, AREA_MINIMA_EM_PORCENTAGEM=0,
                                    ALTURA_MINIMA_EM_PORCENTAGEM=0,LARGURA_MINIMA_EM_PORCENTAGEM=0):
    if BB[3] < LARGURA_MINIMA_EM_PORCENTAGEM:
        return False
    elif BB[4] < ALTURA_MINIMA_EM_PORCENTAGEM:
        return False
    elif (BB[4] * BB[3]) < AREA_MINIMA_EM_PORCENTAGEM:
        return False
    else:
        return True















"""
        FUNÇÕES LEGACY 
            funções antigas, desconsidere para a maior parte dos casos, mas ainda tem utilidade em
            um ou dois casos especificos
"""

## FUNÇÕES PARA LER LABELS EM FORMATO DE LISTAS
# -Aqui estarão funções consideradas "Legacy" para o projeto, em que eram utilizadas a leitura em formato
# de listas ao inves de classes, embora não seja tão utilizado, é mantido por questão de compatibilidade

#   ESTRUTURA DA LISTA DE LABELS
#   labels_lista[x] = cada imagem
#   labels_lista[x][y] = y: 0 -> nome do arquivo de img; y: 1 -> lista com labels
#   labels_lista[x][y][z] = z -> lista do Bounding Box z encontrado na img: [classe, x, y, w, h]

def ler_BBs_de_txt_para_lista(pathDoTxt, LISTA_DE_INDEX_DESEJADOS = []):

    # Define o nome do Txt sem o ".txt" no final, util para pegar a imagem equivalente no futuro
    nome_txt = os.path.basename(pathDoTxt).rsplit(".",1)[0]
    
    # -Caso 1: Em que a lista de index não tem valor nenhum dentro, logo o programa lê todas
    # as classes do arquivo  
    if (not LISTA_DE_INDEX_DESEJADOS):
        with open(pathDoTxt, 'r') as file:
            Lista_de_BBs = [linha.rstrip().split(' ') for linha in file]
        dupla_nome_label = [nome_txt, Lista_de_BBs]
        return dupla_nome_label
    
    # -Caso 2: A lista de index não é vazia e o programa ira procurar adicionar á lista de bounding boxes
    # somente as classs que foram adicionadas na Lista de Index Desejados
    else:
        Lista_de_BBs = []
        with open(pathDoTxt, 'r') as file:
            for linha in file:
                if int(linha[0]) in LISTA_DE_INDEX_DESEJADOS:
                    Lista_de_BBs.append(linha.rstrip().split(' '))
        dupla_nome_label = [nome_txt, Lista_de_BBs]
        return dupla_nome_label
    
    # -Em ambos os casos, a função retorna uma lista [x,y] com x: Nome da imagem/label
    # e y: A lista de bounding boxes nela, com o padrão da lista de BBs sendo:
    # -Lista[1][b] -> b: o index de uma das listas de BBs da imagem
    # -Lista[1][b] -> [Index, Xcentro, Ycentro, Width, Height]


    

def ler_labels_para_lista(pathDasLabels, LISTA_DE_INDEX_DESEJADOS_ = []):
    labels_lista = []

    # -Garante que o codigo so continue caso a lista de index esteja em tipo Integer 
    # e assim não gere problemas de compatibilidade mais para frente no codigo
    if not all([isinstance(item, int) for item in LISTA_DE_INDEX_DESEJADOS_]):
        raise Exception("A lista com index desejados contém valores que não são do tipo Int")
    
    # -Roda a função de obter os BBs de uma imagem em cada arquivo .txt do diretorio dado
    # gerando uma lista com todos os BBs de cada imagem no padrão apresentado no inicio
    # da seção de funções de labels para listas
    for txt in os.listdir(pathDasLabels):
        if txt.endswith(".txt"):
            caminho_txt = os.path.join(pathDasLabels, txt)
            labels_do_txt = ler_BBs_de_txt_para_lista(caminho_txt, LISTA_DE_INDEX_DESEJADOS=LISTA_DE_INDEX_DESEJADOS_)
            labels_lista.append(labels_do_txt)
    return labels_lista




