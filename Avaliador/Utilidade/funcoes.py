import os
from biblioteca_vis.Utils import Geral, GUI_controller, Classes, ManuseioLabels
import pandas as pd


###
###     FUNÇÕES DE SUPORTE
###

#Função para calcular o IOU, recebe um dicionario de BB1 e BB2 como referencia
#Fonte do codigo https://stackoverflow.com/questions/25349178/calculating-percentage-of-bounding-box-overlap-for-image-detector-evaluation
def calcular_iou(bb1,bb2):
    x_left = max(bb1[0], bb2[0])
    y_top = max(bb1[1], bb2[1])
    x_right = min(bb1[2], bb2[2])
    y_bottom = min(bb1[3], bb2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection_area = (x_right - x_left + 1) * (y_bottom - y_top + 1)

    bb1_area = (bb1[2] - bb1[0] + 1) * (bb1[3] - bb1[1] + 1)
    bb2_area = (bb2[2] - bb2[0] + 1) * (bb2[3] - bb2[1] + 1)

    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0

    return iou

#Função para retornar o conjunto de bounding boxes com o maior IOU
#Recebe um bb de referencia e uma lista de bbs para serem comparados
def retorne_maior_iou(bb_referencia, lista_de_bbs_para_teste):
    iou_maior = 0
    for bb_teste in lista_de_bbs_para_teste:
        iou = calcular_iou(bb_referencia[1:], bb_teste[1:])
        if iou >= iou_maior:
            bb_com_maior_iou = bb_teste
            iou_maior = iou
    return bb_com_maior_iou, iou_maior

# A função gera um dicionario com as classes como indices e coloca o valor para cada uma como 0
def gerar_dicionario_para_contagem(dicionario_de_classes, RETORNAR_LISTA_VAZIA = False):
    dicionario_contagem = {}
    for classe in dicionario_de_classes.keys():
        if RETORNAR_LISTA_VAZIA:
            dicionario_contagem[classe] = []
        else:
            dicionario_contagem[classe] = 0
    return dicionario_contagem

#Função para transformar todas as Classes de labels de padrão WHXY para XYXY
def batch_wh2xy(lista_de_labels):
    nova_lista_de_labels = []
    for label in lista_de_labels:
        novo_label = label.transformar_padrão_labels(MODO_A_TRANSFORMAR_WH_ou_XY = "XY")
        nova_lista_de_labels.append(novo_label)
    return nova_lista_de_labels

#Função para retornar um dicionario com a soma dos numeros de 2 dicionarios
def _soma_dicionarios(dicionario_base, dicionario_a_somar):
    assert len(dicionario_base.keys()) == len(dicionario_a_somar.keys()), "Os dicionarios somados não possuem a mesma quantidade de indices"
    dicionario_resultante = {}
    for key in dicionario_base.keys():
        dicionario_resultante[key] = dicionario_base[key] + dicionario_a_somar[key]
    return dicionario_resultante

#Função para retornar um dicionario com o append 
def _append_dicionarios(dicionario_base, dicionario_a_somar):
    assert len(dicionario_base.keys()) == len(dicionario_a_somar.keys()), "Os dicionarios appendados não possuem a mesma quantidade de indices"
    dicionario_resultante = dicionario_base
    for key in dicionario_base.keys():
        Skey = str(key)
        for achado in dicionario_a_somar[Skey]:
            dicionario_resultante[Skey].append(achado)
    return dicionario_resultante

#Função para transformar um dict no formato que é requerido para gerar a matriz de confusão em df
#o formato é o lista de listas para representar colunas e linhas da matriz ja transformado em df do pandas
def dic2MC_PD(dicionario,dic_classes):
    lista_matriz = []
    for linha in dicionario.keys():
        lista_linha = []
        for coluna in dicionario.keys():
            contador = 0
            for valor in dicionario[linha]:
                if str(valor) == coluna:
                    contador += 1
            lista_linha.append(contador)
        lista_matriz.append(lista_linha)
    #Aqui a lista_matriz ja esta organizada em listas de listas de linhas
    df_cm = pd.DataFrame(lista_matriz,index = [dic_classes[i] for i in dicionario.keys()],
                  columns = [dic_classes[i] for i in dicionario.keys()])

    return df_cm


##
##      FUNÇÕES PRINCIPAIS
##

# A função lida com as labels de uma imagem, comparando duas listas de labels dessa mesma imagem(a referencia e a ser testada)
# e retorna os bounding_boxes que forem corretamente classificados e localizados por classe em formato de dicionario
def relatorio_geral(lista_referencia, lista_teste, dicionario_de_classes,LIMITE_IOU_ACEITO = 0.5, SO_CONSIDERA_CLASSES_IGUAIS = True):
    #Cria um dicionario de acertos para salvar os acertos e retornar depois
    #Depois cria um dicionario de referencia para ser comparado depois
    dicionario_de_acertos = {}
    dicionario_referencia = {}
    #Passa as classes do dicionario de referencia para o dicionario de acertos e coloca-os como 0
    for classe in dicionario_de_classes.keys():
        dicionario_de_acertos[classe] = 0
        dicionario_referencia[classe] = 0
    #Cicla entre todos os labels do arquivo
    for bounding_box_ref in lista_referencia:
        #Registra o boundingBox para o dic de referencia para comparar depois
        dicionario_referencia[bounding_box_ref[0]] = dicionario_referencia[bounding_box_ref[0]] + 1
        for bounding_box_test in lista_teste:
            if (bounding_box_ref[0] != bounding_box_test[0]) and (SO_CONSIDERA_CLASSES_IGUAIS):
                continue
            iou = calcular_iou(bounding_box_ref[1:],bounding_box_test[1:])
            if iou >= LIMITE_IOU_ACEITO:
                dicionario_de_acertos[bounding_box_ref[0]] = dicionario_de_acertos[bounding_box_ref[0]] + 1
                break
    return dicionario_de_acertos, dicionario_referencia










##FAZER A PARTE DE MATRIZ DE CONFUSÃO
#COMO APLICAR:
#1- Carrega uma lista_de_BBs_referencia e uma lista_de_BBs_para_validar de uma imagem e transforma de WH para XY
#2- Aplica um nested for loop 2x, ou seja, avalia para uma bounding box da referencia com todos os para ser testado
#e com isso aplica o calculo de IOU em cada um , o que tiver o maior valor passa para a etapa 3
#(PS.: um valor minimo deve ser escolhido para que caso exista um IOU que toca por acaso nas cordenadas e fica 0.10
# nao seja considerado)
#3- com o conjunto de BBs com o maior IOU escolhida, vê qual foi a classificação (vulgo, qual foi o index dela)
#4- cria dois dics com as classes como chave, um dic_referencia e um dic_classificado
#5- com esses dois já escolhidos, podemos passar para a parte em que é passado para o plt.show

def _retorna_dicionario_labels_matriz(lista_referencia, lista_teste, dicionario_de_classes,LIMITE_IOU_ACEITO = 0.5):
    dicionario_esperado_achado = gerar_dicionario_para_contagem(dicionario_de_classes,RETORNAR_LISTA_VAZIA=True)
    dicionario_referencia = gerar_dicionario_para_contagem(dicionario_de_classes)
    print(dicionario_esperado_achado)
    #Cicla entre todos os labels do arquivo
    for bounding_box_ref in lista_referencia:
        #Registra o boundingBox para o dic de referencia para comparar depois
        key_ref = str(bounding_box_ref[0])
        dicionario_referencia[key_ref] = dicionario_referencia[key_ref] + 1
        bb_localizada,iou = retorne_maior_iou(bounding_box_ref,lista_teste)
        #Se o iou for menor que o limite minimo ele ignora esse bounding box (dizendo que nao existe)
        if iou <= LIMITE_IOU_ACEITO:
            #Nesse caso, não foi achado um bb valido, assim é adicionado como Falso Negativo(indice = -1) na lista de teste
            dicionario_esperado_achado[key_ref].append(-1)
            continue
        print(type(dicionario_esperado_achado[key_ref]))
        dicionario_esperado_achado[key_ref].append(bb_localizada[0])
    return dicionario_esperado_achado, dicionario_referencia

#Função para retornar um dicionario para gerar a matriz de confusão a partir de uma lista de labels de um diretorio inteiro
def retorna_dicionario_matriz_confunsao(lista_labels_referencia, lista_labels_para_avaliar,dicionario_classes,LIMITE_IOU_ACEITO = 0.75):
    dicionario_resultante_matriz = gerar_dicionario_para_contagem(dicionario_classes, RETORNAR_LISTA_VAZIA=True)
    dicionario_resultante_ref = gerar_dicionario_para_contagem(dicionario_classes)
    for imagem_referencia in lista_labels_referencia:
        for imagem_avaliar in lista_labels_para_avaliar:
            if imagem_referencia.nome != imagem_avaliar.nome:
                continue
            dic_matriz_imagem,dic_referencia_imagem = _retorna_dicionario_labels_matriz(imagem_referencia.lista_de_BBs, imagem_avaliar.lista_de_BBs, dicionario_classes, LIMITE_IOU_ACEITO=LIMITE_IOU_ACEITO)
            dicionario_resultante_matriz = _append_dicionarios(dicionario_resultante_matriz, dic_matriz_imagem)
            dicionario_resultante_ref = _soma_dicionarios(dicionario_resultante_ref, dic_referencia_imagem)

    return dicionario_resultante_matriz, dicionario_resultante_ref