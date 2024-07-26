##
##  Script para a etapa de padronização do tratamento do dataset
##

# IMPORTS
from Scripts.redimencionarRapido import *

# INPUT DO PATH PARA SER LIDO
_path = input("Qual o diretorio do dataset a ser padronizado (somente imagens)?: \n")

#EXECUTA AS FUNÇÕES
RedimencionarRextensao(_path)

#PRONTO
a = input("Pronto! Pressione enter para continuar...")