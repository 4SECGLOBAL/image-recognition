##
##
##      Script para Copiar somente arquivos de uma pasta quando uma segunda pasta
##          de refetencia tambem contem tal arquivo
##

#   IMPORTS
import json

if __name__ == "__main__":  
    print("Esse arquivo não foi feito para ser rodado individualmente")
    a = input("Aperte enter para sair...")
    exit()
#Esse if protege o arquivo de ser rodado sem ser chamado por outro script


class json_Classes:
    def __init__(self, dicionario_de_classes, arquivo_nome = "classes.json"):
        self.dicionario_de_classes = dicionario_de_classes
        self.arquivo_nome = arquivo_nome

    def __str__(self):
        str_json = json.dumps(self.dicionario_de_classes, indent=2)
        return str_json

    def retorna_dicionario(self):
        return self.dicionario_de_classes
    
    def atualiza_dicionario(self, dicionario_de_classes):
        self.dicionario_de_classes = dicionario_de_classes
    
    def carregar_arquivo_json_dicionario(self):
        path_arquivo = self.arquivo_nome
        with open(path_arquivo, 'r') as arq:
            dados = json.load(arq)
        self.dicionario_de_classes = dados
    
    def salvar_arquivo_json_dicionario(self):
        path_arquivo = self.arquivo_nome
        with open(path_arquivo, 'w') as arq:
            json.dump(self.dicionario_de_classes, arq, indent=4)
    
    def _converter_keys_string2int(self):
        for Key in self.dicionario_de_classes.keys():
            self.dicionario_de_classes[int(Key)] = self.dicionario_de_classes.pop(Key)
    
