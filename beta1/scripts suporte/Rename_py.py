import os
import shutil
from progress.bar import Bar


# Pasta com imagens
pasta_imagens = r'C:\Users\gabri\Desktop\MODELOFINAL\beta1\beta1\train\images2'
# Pasta com arquivos txt
pasta_txt = r'C:\Users\gabri\Desktop\MODELOFINAL\beta1\beta1\train\labels'

# Listar arquivos nas pastas
imagens = os.listdir(pasta_imagens)
txt_files = os.listdir(pasta_txt)

# Garantir que apenas arquivos de imagem e txt são considerados
imagens = [arquivo for arquivo in imagens]
txt_files = [arquivo for arquivo in txt_files if arquivo.endswith('.txt')]
nomes_arquivos = {}

# Listar arquivos na pasta
i = 0
for arquivo in os.listdir(pasta_txt):
    nomes_arquivos[arquivo.rsplit(".",1)[0]] = str(i) + "_g"
    i = i + 1

bar = Bar('Processing', max=len(imagens))
# Renomear os arquivos
for ind in nomes_arquivos.keys():
    bar.next()
    novo_nome_imagem = f"{nomes_arquivos[ind]}.jpg"  # Nome da imagem como número crescente
    novo_nome_txt = f"{nomes_arquivos[ind]}.txt"  # Mesmo nome para o arquivo de texto

    caminho_imagem_antigo = os.path.join(pasta_imagens, "{}.jpg".format(ind))
    caminho_imagem_novo = os.path.join(pasta_imagens, novo_nome_imagem)

    caminho_txt_antigo = os.path.join(pasta_txt, "{}.txt".format(ind))
    caminho_txt_novo = os.path.join(pasta_txt, novo_nome_txt)

    # Renomear os arquivos
    try:
        shutil.move(caminho_imagem_antigo, caminho_imagem_novo)
        shutil.move(caminho_txt_antigo, caminho_txt_novo)
    except:
        print("Error no " + ind)
bar.finish()
print("Arquivos renomeados com sucesso!")