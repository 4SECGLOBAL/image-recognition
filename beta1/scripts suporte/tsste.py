import os

# Pega o diretorio para executar o script
directory = input("Qual o diretorio do dataset para remover os Augmentations?")

# Passa pelos arquivos em um diretorio
for filename in os.listdir(directory):
    if "AUG" in filename:
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Arquivo '{filename}' visto como augmentation foi deletado.")

print("Pronto!")
