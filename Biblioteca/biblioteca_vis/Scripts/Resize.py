from PIL import Image
import os
from progress.bar import Bar

# Pasta de entrada com as imagens originais
pasta_entrada = r'C:\Users\gabri\Desktop\MODELOFINAL\beta1\beta1\train\images'

# Pasta de saída para as imagens redimensionadas
pasta_saida = r'C:\Users\gabri\Desktop\MODELOFINAL\beta1\beta1\train\images2'

# Garantir que a pasta de saída existe
if not os.path.exists(pasta_saida):
    os.makedirs(pasta_saida)
bar = Bar('Processing', max=len(os.listdir(pasta_entrada)))
# Listar os arquivos de imagem na pasta de entrada
for arquivo in os.listdir(pasta_entrada):
    caminho_entrada = os.path.join(pasta_entrada, arquivo)
    caminho_saida = os.path.join(pasta_saida, (arquivo.rsplit(".",1)[0] + ".jpg"))

    # Abrir a imagem original
    imagem = Image.open(caminho_entrada)

    # Calcular a nova largura com base na altura de 480 pixels e no aspect ratio original
    largura_original, altura_original = imagem.size
    nova_largura = int(480 * (largura_original / altura_original))

    # Redimensionar a imagem
    imagem = imagem.resize((nova_largura, 480)).convert('RGB')

    # Salvar a imagem redimensionada como JPEG
    imagem.save(caminho_saida, "JPEG")
    bar.next()
bar.finish()
print("Imagens redimensionadas e salvas com sucesso!")
