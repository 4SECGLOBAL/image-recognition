##
##
##      Script para Copiar somente arquivos de uma pasta quando uma segunda pasta
##          de refetencia tambem contem tal arquivo
##

#   IMPORTS
import json, os
from Utils.json_class import *
from Utils.GUI_controller import *

#   DEFINES
CWD = os.path.dirname(os.getcwd())
NOME_JSON_ORDEM_CLASSES = "classes.json"
PATH_JSON_CLASSES = os.path.join(CWD, NOME_JSON_ORDEM_CLASSES)

#   VARIAVEIS
classes = Classes(None)
controlador = Controlador_GUI()

"""
if __name__ == "__main__":  
    print("Esse arquivo não foi feito para ser rodado individualmente")
    a = input("Aperte enter para sair...")
    exit()
#Esse if protege o arquivo de ser rodado sem ser chamado por outro script
"""



#MENU
print("\n")
controlador.titulo("CONFIGURAÇÃO DAS CLASSES", bLargura=50,tempo=0.075)
linhas_Consumidas_menu = 8
sleep(0.1)
controlador.titulo("~(1)Ler .Json~~(2)Modificar Json~~(3)Criar Json~", bLargura=30, bAltura=8, cTop=False, simb="/", tempo=0.075)
print("")
In = input("Qual a seleção?\n")
if In == "1":
    print(classes)
#elif In == '3':
    #classes.salvar_arquivo_json_dicionario(NOME_JSON_ORDEM_CLASSES)


controlador.limpar_linhas(3,tempo=0.15)
a = input("Aperte enter...")