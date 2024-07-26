import os
from biblioteca_vis.Utils import Geral, GUI_controller, Classes, ManuseioLabels


class ablueblueblue:
    def __init__(self, PATH_LABELS = "/REFERENCIA/labels"):
        #Carrega um diretorio em uma lista
        self.Labels = ManuseioLabels.lerLabelsDir(PATH_LABELS)

    #Transforma a lista de BBs em um dic
    def _trans(lista):
        dic = {
            'x1': lista[0],
            'y1': lista[1],
            'x2': lista[2],
            'y2': lista[3]
            }
        return dic


