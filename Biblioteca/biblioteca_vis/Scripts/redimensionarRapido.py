##
##  Script para redimensionar e mudar a extensão do dataset
##

from PIL import Image
import os
from progress.bar import Bar

def redimensionarRextensao(pasta_entrada):
    pasta_saida = pasta_entrada + "_PADRONIZADO"
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
    bar = Bar('Processing', max=len(os.listdir(pasta_entrada)))

    for arquivo in os.listdir(pasta_entrada):
        caminho_entrada = os.path.join(pasta_entrada, arquivo)
        caminho_saida = os.path.join(pasta_saida, (arquivo.rsplit(".",1)[0] + ".jpg"))

        imagem = Image.open(caminho_entrada)

        # Calcular a nova largura com base na altura de 480 pixels e no aspect ratio original
        largura_original, altura_original = imagem.size
        nova_largura = int(480 * (largura_original / altura_original))

        imagem = imagem.resize((nova_largura, 480)).convert('RGB')

        imagem.save(caminho_saida, "JPEG")
        bar.next()
    bar.finish()
    print("Imagens redimensionadas e salvas com sucesso!")
