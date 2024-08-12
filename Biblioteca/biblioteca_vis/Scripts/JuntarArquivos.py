import os, argparse, shutil
from progress.bar import Bar
import Utils.Geral
from PIL import Image


##  PARTE DO MAIN
#Função principal
def j_a(arquivo1, arquivo2, arquivo_saida):
    if not os.path.exists(arquivo2):
        shutil.copy(arquivo1, arquivo_saida)
        return
    try:
        with open(arquivo1, 'r') as file1, open(arquivo2, 'r') as file2, open(arquivo_saida, 'w') as output_file:
            # Lê o conteúdo do primeiro arquivo e escreve no arquivo de saída
            output_file.write(file1.read())
            # Lê o conteúdo do segundo arquivo e escreve no arquivo de saída
            output_file.write(file2.read())
    except IOError:
        print("Erro ao ler ou escrever arquivos.")

def JuntarTodosArquivos(path_arquivos1, path_arquivos2, path_novos_arquivos):
    #Cria pasta caso não exista
    path_novos_arquivos = Utils.Geral.criar_diretorio(path_novos_arquivos,ADD_SUFIXO_SE_EXISTIR=True)

    #Carrega os nomes de arquivos .txt na lista
    arquivos_base = Utils.Geral.ler_arquivos_de_um_diretorio(path_arquivos1,REMOVER_PONTO_EXTENSAO=False,
                                               PASSAR_EXTENSOES_ESPECIFICAS=['txt'],
                                               MANTER_PATH_COMPLETO=False)
    
    
    bar = Bar('Juntando...', fill='#', max = (len(arquivos_base)), suffix='%(percent)d%%') 
    for arq in arquivos_base:
        arquivo1 = os.path.join(path_arquivos1, arq)
        arquivo2 = os.path.join(path_arquivos2, arq)
        arquivo_save = os.path.join(path_novos_arquivos, arq)
        j_a(arquivo1, arquivo2, arquivo_save)
        bar.next()
    bar.finish()

 


if __name__ == "__main__":
    ##  PARSER
    ap = argparse.ArgumentParser(description="redimensiona todas as imagens de uma pasta para uma altura padrão")
    ap.add_argument("-p", "--Path", required=False,default=' ',
        help="Caminho da pasta em que as imagens estão localizadas")
    ap.add_argument("-a", "--AlturaFixa", required=False,default=' ',
        help="Altura padrão a ser adotada por todas as imagens; Padrão = 640")
    args = ap.parse_args()

    # Checa se não conter parser para adicionar manualmente
    _cwd = os.getcwd()
    if args.Path == ' ':
        Path = input("Qual a pasta em que as imagens estão localizadas?\n")
        _Path = os.path.join(_cwd, Path)
    else:
        _Path = args.Path
    
    if args.AlturaFixa == ' ':
        AlturaFixa = int(input("Qual a altura padrão a ser adotada por todas as imagens?\n"))
    else:
        AlturaFixa = int(args.Path)

    #redimensionarImagens(_Path, ALTURA_FIXA=AlturaFixa)