##
##  Script para a etapa final de limpeza do tratamento do dataset
##

# IMPORTS
import os
from progress.bar import Bar

# INPUT DO PATH PARA SER LIDO
_path = input("Qual o diretorio do dataset a ser padronizado (somente imagens)?: \n")

bar = Bar('Renomeando', fill='@', suffix='%(percent)d%%', max=len(os.listdir(_path)))

for index, file in enumerate(os.listdir(_path)):
    file_path = os.path.join(_path, file)
    
    file_extension = os.path.splitext(file)[1]

    novo_nome = str(index) + "__g_" + file_extension
    

    os.rename(file_path, os.path.join(_path, novo_nome))

#PRONTO
a = input("Pronto! Pressione enter para continuar...")