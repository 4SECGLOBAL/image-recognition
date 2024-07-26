import os, shutil
from progress.bar import Bar
from PIL import Image
from Utils.Classes import *

"""
            FUNÇÕES DE TRANSFORMADAS DE DADOS  
            -Essa seção é responsavel por criar funções para manusear ou transformar dados
            e imagens, é usado principalmente como funções de suporte
"""

## FUNÇÃO DE TRANSFORMADA DE X1Y1X2Y2 PARA XYWH E VICE-VERSA

def wh2xy(x_center,y_center,w,h):
    x1, y1 = x_center-w/2, y_center-h/2             # Gera os pontos no topo a esquerda
    x2, y2 = x_center+w/2, y_center+h/2             # Gera os pontos na parte inferior a direita
    return [x1, y1, x2, y2]

def xy2wh(x1,y1,x2,y2):
    center_x, center_y = (x1 + x2)/2 , (y1 + y2)/2  # Gera os pontos de centro XY do BB
    width, height = x2 - x1, y2 - y1                # Gera a o tamanho de largura e altura do BB
    return [center_x, center_y, width, height]



"""
## FUNÇÕES PARA LER LABELS EM FORMATO DE CLASSE
# -> Lê um txt de labels de uma imagem e salva eles em uma classe de imagem + labels
# -> Em seguida, na segunda função, todos os txt de um diretorio são lidos e retorna em uma
#    lista de 
"""

def lerLabelsTxt(pathDoTxt):
    # Define o nome do Txt sem o ".txt" no final, util para pegar a imagem equivalente no futuro
    nome_txt = os.path.basename(pathDoTxt).rsplit(".",1)[0]
    # 
    Lista_de_BBs = [] 
    with open(pathDoTxt, 'r') as file:
        for BB in file:
            BB_lista = BB.rstrip().split(' ')
            BB_lista[0] = int(BB_lista[0])
            BB_lista[1:] = list(map(float, BB_lista[1:]))
            Lista_de_BBs.append(BB_lista)           
    dupla_nome_label = vis_Imagem_Labels(nome_txt, Lista_de_BBs)
    return dupla_nome_label
# -Afunção retorna uma lista [x,y] com x: Nome da imagem/label
# e y: A lista de bounding boxes nela, com o padrão da lista de BBs sendo:
# -Lista[1][b] -> b: o index de uma das listas de BBs da imagem
# -Lista[1][b] -> [Index, Xcentro, Ycentro, Width, Height]


###  Função para ler os txt para o label de um diretorio todo
def lerLabelsDir(pathDasLabels):
    labels_lista = []
    # -
    for txt in os.listdir(pathDasLabels):
        if txt.endswith(".txt"):
            caminho_txt = os.path.join(pathDasLabels, txt)
            labels_do_txt = lerLabelsTxt(caminho_txt)
            labels_lista.append(labels_do_txt)
    return labels_lista



### FUNÇÃO PARA PEGAR UM TXT DE LABEL E ESCREVE EM FORMATO TXT
def listaBBsParaTxt(pathComNomeTxt, lista_de_BBs = []):
    with open(pathComNomeTxt, 'w') as txt:
        for BB in lista_de_BBs:
            linha = f"{str(BB[0])} {str(BB[1])} {str(BB[2])} {str(BB[3])} {str(BB[4])}"
            txt.write(linha + "\n")




### FUNÇÃO PARA RETORNAR UMA LISTA DE LABELS FILTRADAS COM OS INDICES DE INTERESSE
def filtrarLabels(cls_imagem_label, lista_de_index):
        lista_BBs_filtrada = []
        for BB in cls_imagem_label.lista_de_BBs:
            if int(BB[0]) in lista_de_index:
                lista_BBs_filtrada.append(BB)
        return lista_BBs_filtrada







































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
