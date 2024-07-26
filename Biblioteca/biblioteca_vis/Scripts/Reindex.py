import os

# Pasta com arquivos TXT
pasta_txt = r"C:\Users\gabri\Desktop\project-29-at-2023-11-24-02-06-97a40367\labels"

# Listar arquivos na pasta
for arquivo in os.listdir(pasta_txt):
    if arquivo.endswith('.txt'):
        caminho_arquivo = os.path.join(pasta_txt, arquivo)

        # Abra o arquivo original para leitura
        with open(caminho_arquivo, "r") as arquivo_txt:
            linhas = arquivo_txt.readlines()

        # Abra o arquivo para escrita
        with open(caminho_arquivo, "w") as arquivo_txt:
            for linha in linhas:
                palavras = linha.split()
                if palavras:
                    try:
                        palavras[0] = "6"
                    except ValueError:
                        pass  # Ignorar linhas que não começam com um número
                arquivo_txt.write(" ".join(palavras) + "\n")

print("Substituição concluída: O primeiro número de cada linha foi alterado para 8.")