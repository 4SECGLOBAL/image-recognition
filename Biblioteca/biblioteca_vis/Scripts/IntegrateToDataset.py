import os
import shutil
from progress.bar import Bar
from Biblioteca.biblioteca_vis.Scripts.IncorporarDataset import *


def IntegrarDataset(path_dataset_original, path_integrar):
    if ChecarSeDataset(path_integrar):
        #Caso o diretorio dado já seja a pasta com o dataset
        IncorporaDataset(path_integrar, path_dataset_original)
    else:
        #Caso o diretorio seja uma pasta com diversos datasets       
        for arquivo in os.listdir(path_integrar):
            path_arquivo = os.path.join(path_integrar, arquivo)
            if os.path.isdir(path_arquivo):
                if ChecarSeDataset(path_arquivo):
                    #Aqui garante que a pasta "nested" representa um dataset
                    IncorporaDataset(path_arquivo, path_dataset_original)
                else:
                    # Neste caso, caso não seja, busca se existe algum dataset "nesteado" dentro da pasta
                    IntegrarDataset(path_dataset_original, path_arquivo)
    return
            


def ChecarSeDataset(path_dataset):
    lista_arquivos = [x for x in os.listdir(path_dataset)]
    if ("labels" in lista_arquivos) and ("images" in lista_arquivos):
        return True
    else:
        print("Pasta nao representa dataset: {}".format(path_dataset))
        return False

def transcreverDataset(path_dataset):
    path_labels = os.path.join(path_dataset, "labels")
    path_images = os.path.join(path_dataset, "images")

    lista_transcrita = []

    for label in os.listdir(path_labels):
        nome_arquivo = label.rstrip(".txt")
        path_conjunto_label = os.path.join(path_labels, nome_arquivo+".txt")
        path_conjunto_image = os.path.join(path_images, nome_arquivo+".jpg")

        lista_transcrita.append((path_conjunto_image, path_conjunto_label))
    
    return lista_transcrita
