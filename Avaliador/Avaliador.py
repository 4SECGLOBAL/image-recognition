##
##
##      Script para Copiar somente arquivos de uma pasta quando uma segunda pasta
##          de refetencia tambem contem tal arquivo
##

#   IMPORTS
import os
from Utilidade.json_class import json_Classes
from Utilidade.funcoes import *
from biblioteca_vis.Utils import Geral, GUI_controller, Classes, ManuseioLabels
import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt



#   DEFINES
CWD = os.getcwd()
PATH_REFERENCIAS_LABELS = os.path.join(CWD, r"REFERENCIA\labels")
PATH_RESULTADOS = os.path.join(CWD, r"RESULTADOS")
LIMITE_IOU = 0.64
classes = json_Classes(None)
classes.carregar_arquivo_json_dicionario()
print(type(classes.retorna_dicionario()))
print(classes.retorna_dicionario())


#   START
Nome_Versao = input("Qual o nome da versão a ser salva?:\n")
PATH_SAVE_VERSAO = os.path.join(PATH_RESULTADOS, Nome_Versao)
PATH_LABELS_PARA_TESTAR = input("Qual o path das labels para testar?")#r'C:\Users\gabri\Documents\LABIC\Projeto_Visao_4\yolov7\runs\test\TESTE4\labels'#input("Qual o diretorio da pasta de labels para ser testada?:\n")




#   MAIN CODE
lista_labels_referencia = batch_wh2xy(ManuseioLabels.lerLabelsDir(PATH_REFERENCIAS_LABELS))
lista_labels_para_avaliar = batch_wh2xy(ManuseioLabels.lerLabelsDir(PATH_LABELS_PARA_TESTAR))



dicionario_matriz, dicionario_referencia = retorna_dicionario_matriz_confunsao( lista_labels_referencia, lista_labels_para_avaliar,
                                                                                classes.retorna_dicionario(), LIMITE_IOU_ACEITO=LIMITE_IOU )

df_matriz = dic2MC_PD(dicionario_matriz,classes.retorna_dicionario())
print(df_matriz)
sn.set(font_scale=1.4) # for label size
sn.heatmap(df_matriz, annot=True, annot_kws={"size": 16}) # font size
plt.xlabel("Verdadeiro")
plt.ylabel("Inferido")
plt.title("Matrix de Confusao")


plt.show()


a = input("Pressiona enter...")
