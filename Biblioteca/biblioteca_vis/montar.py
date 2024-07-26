import os
import shutil
from progress.bar import Bar

def _copiaDiretorioSePasta(origem, pasta_desejada):
    lista_pastas_diretorio = []
    for pasta in os.listdir(origem):
        pasta_path = os.path.join(origem, pasta)           
        if os.path.isdir(pasta_path):
            if pasta == pasta_desejada:
                lista_pastas_diretorio.append(pasta_path)
            else:
                lista_pastas_diretorio = lista_pastas_diretorio +_copiaDiretorioSePasta(pasta_path, pasta_desejada=pasta_desejada)
    return lista_pastas_diretorio

def copiar_pastas(origem, destino, pasta_desejada):
    # Lista todas as pastas no diretório de origem
    lista_pastas =_copiaDiretorioSePasta(origem, pasta_desejada)

    print("INICIANDO A COPIA DE {}".format(pasta_desejada))
    bar = Bar('Copiando', max=len(lista_pastas))

    # Cria o diretório de destino se não existir
    if not os.path.exists(destino):
        os.makedirs(destino)

    # Itera sobre as pastas encontradas e copia o conteúdo para o diretório de destino
    for pasta in lista_pastas:
        shutil.copytree(pasta, destino, dirs_exist_ok=True)
        bar.next()
    bar.finish()

if __name__ == "__main__":
    cwd = os.getcwd()

    # Diretório de origem
    diretorio_origem = input("Qual o diretorio do dataset a ser montado?")

    # Diretório de destino para as pastas de imagens
    nome_dataset = input("Qual o nome do dataset a ser montado?")
    diretorio_montado = os.path.join(cwd,"DATASETS_MONTADOS")
    diretorio_destino = os.path.join(diretorio_montado ,nome_dataset)

    # Nome das pastas a serem copiadas
    nome_pasta_images = "images"
    nome_pasta_labels = "labels"

    # Define o path para as pastas
    path_pasta_images = os.path.join(diretorio_destino, nome_pasta_images)
    path_pasta_labels = os.path.join(diretorio_destino, nome_pasta_labels)

    # Executa o codigo
    copiar_pastas(diretorio_origem, path_pasta_images, nome_pasta_images)
    copiar_pastas(diretorio_origem, path_pasta_labels, nome_pasta_labels)

    print("Cópia concluída.")
