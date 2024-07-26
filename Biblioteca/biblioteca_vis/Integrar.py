##
##  Script para a etapa de integração do dataset
##

# IMPORTS
from Scripts.IntegrateToDataset import *

# INPUT DO PATH PARA SER LIDO
_path_original = input("Qual o diretorio do dataset que recebera a integração (o original)?: \n")
_path_pasta_com_datasets = input("Qual o diretorio da pasta com os datasets que serão adicionados ao dataset original?: \n")

#EXECUTA AS FUNÇÕES
IntegrarDataset(_path_original, _path_pasta_com_datasets)

#PRONTO
a = input("Pronto! Pressione enter para continuar...")