import os

# Pasta com imagens
pasta_imagens = r'C:\Users\gabri\Desktop\MODELOFINAL\beta1\beta1\train\images2'
# Pasta com arquivos txt
pasta_txt = r'C:\Users\gabri\Desktop\MODELOFINAL\beta1\beta1\train\labels'
# Listar arquivos nas pastas
imagens = set([arquivo.rsplit('.',1)[0] for arquivo in os.listdir(pasta_imagens)])
txt_files = set([arquivo.rsplit('.',1)[0] for arquivo in os.listdir(pasta_txt)])


# Encontrar os arquivos que não têm correspondência em ambas as pastas
arquivos_para_excluir = (imagens - txt_files) | (txt_files - imagens)
print((txt_files - imagens))
# Excluir os arquivos que não têm correspondência
a = input("Enter para continuar...")
for arquivo in arquivos_para_excluir:
    if arquivo in imagens:
        caminho_imagem = os.path.join(pasta_imagens, arquivo + '.jpg')
        os.remove(caminho_imagem)
    if arquivo in txt_files:
        caminho_txt = os.path.join(pasta_txt, arquivo + '.txt')
        os.remove(caminho_txt)

print("Arquivos sem correspondência excluídos com sucesso!")

