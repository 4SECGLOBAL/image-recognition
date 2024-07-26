##
##  Script para a etapa de limpeza do tratamento do dataset
##

# IMPORTS
from Scripts.limpaPorExtensao import *
from Scripts.removePorTamanho import *
from Scripts.RemoveDuplicata import *
from Scripts.deletarWandB import *

# INPUT DO PATH PARA SER LIDO
_path = input("Qual o diretorio do dataset a ser limpo (somente imagens)?: \n")

#EXECUTA AS FUNÇÕES
RemoverPorTipo(_path)
RemoverImagensPequenas(_path)
RemoverDuplicata(_path)
RemoverPretoEBranco(_path)

#PRONTO
a = input("Pronto! Pressione enter para continuar...")