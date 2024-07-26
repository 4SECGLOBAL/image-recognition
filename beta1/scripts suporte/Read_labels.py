import os
from progress.bar import Bar

# Defina o caminho da pasta contendo os arquivos de texto
pasta = r"C:\Users\gabri\Desktop\MODELOFINAL\beta1\beta1\train\labels"

# Inicialize um dicionário para armazenar as contagens dos números
contagens = {}
bar = Bar('Processing', max=len(os.listdir(pasta)))
# Percorra todos os arquivos na pasta
for arquivo in os.listdir(pasta):
    if arquivo.endswith(".txt"):
        caminho_arquivo = os.path.join(pasta, arquivo)
        
        # Abra o arquivo e leia linha por linha
        with open(caminho_arquivo, "r") as arquivo_txt:
            for linha in arquivo_txt:
                # Tente extrair o primeiro número de cada linha
                try:
                    numero = int(linha.split()[0])  # Supomos que os números estejam separados por espaços
                    # Atualize a contagem no dicionário
                    if numero in contagens:
                        contagens[numero] += 1
                    else:
                        contagens[numero] = 1
                except (ValueError, IndexError):
                    pass  # Ignorar linhas sem números válidos
    bar.next()
bar.finish()
print(contagens)
# Exiba o dicionário de contagens
for numero, contagem in contagens.items():
    print(f"ID:{numero} = {contagem}")
a=input("Pressione enter para continuar...")