import os, time, bs4,random, requests, shutil
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

## CAMINHOS

# Caminho do diretório do script
_cwd = os.path.dirname(os.path.abspath(__file__))
# Caminho dos executáveis do chrome e chromedriver
chromedriver_path = os.path.join(_cwd, "chromedriver.exe")
chromepath = os.path.join(_cwd, "chrome-win64", "chrome.exe")
# Configuracao dos diretorios Classes, Downloads e Txt_Files (com as frases de busca)
_save = "Classes"
if not os.path.isdir(_save):
    os.makedirs(_save)
_Downloads = os.path.join(_cwd, "Downloads")
if not os.path.isdir(_Downloads):
    os.makedirs(_Downloads)
_Txts = os.path.join(_cwd, "Txt_Files")
if not os.path.isdir(_Txts):
    os.makedirs(_Txts)

## OPCOES DO CHROMEDRIVER
options = webdriver.ChromeOptions()
options.binary_location = chromepath
options.add_argument("--headless")  # Rodar Chrome sem GUI
options.add_argument("--disable-gpu")  # Disabilitar aceleração com GPU
options.add_argument(f"executable_path={chromedriver_path}")  # Caminho do executavel chromedriver
#options.add_extension('Download-All-Images.crx')

##
##
##  MAIN
##
##

projeto = input("Qual o nome do projeto?\n")
_projeto = os.path.join(_save,projeto)
if not os.path.isdir(_projeto):
    os.makedirs(_projeto)

# Capturar a fonte das chaves de pesquisa (arquivo txt ou entrada pelo terminal)
query_lista = []

key_log = int(input("Deseja ler de um arquivo txt? (0 - Não, 1 - Sim)\n"))
if key_log == 1:
    query_in = input("Qual o nome do txt? \n")
    with open(os.path.join(_Txts, query_in+".txt")) as file:
        for line in file:
            query_lista.append(line.rstrip())
            print(line.rstrip())
elif key_log == 0:
    query_in = input("Qual os querys?(0 finaliza): ")
    while query_in != "0":
        query_lista.append(query_in)
        query_in = input("Qual os querys?(0 finaliza): ")

# Capturar o número de expansões da página de busca (quantas imagens possíveis)
max_pgn = int(input("Quantas pgns no maximo: "))

# Inicializar o chromedriver
driver = webdriver.Chrome(options=options)

for q in query_lista:  
    # Acessar URL do google images
    driver.get(f"https://www.google.com/imghp?hl=pt")

    # Localiza a barra de pesquisa e faz a busca pelo query (a chave)
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(q)
    search_box.send_keys(Keys.RETURN)
    
    sleep(8)

    # Expandir até {max_pgn} número de páginas
    for i in range(0, max_pgn):
        # Desce até o final da página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)

        # Encontra as imagens na página
        images = driver.find_elements(By.CLASS_NAME, "rg_i")
        print(images)

        # Download das imagens encontradas na página
        for index, image in enumerate(images):
            try:
                image_url = image.get_attribute("src")
                if image_url:
                    response = requests.get(image_url)
                    with open(f'Downloads/{q}_{index}.jpg', 'wb') as file:
                        file.write(response.content)
                    print(f"Downloaded {q}_{index}.jpg")
            except Exception as e:
                print(f"Nao foi possivel realizar o download de {q}_{index}.jpg - {e}")
    
sleep(2)

print("FINALIZADO OS QUERIES")
pause = input("Aperte enter para começar a mover as imagens para a pasta de projeto...")
driver.quit()

for rar in os.listdir(_Downloads):
    _rar = os.path.join(_Downloads,rar)
    _savecls = os.path.join(_projeto,rar)
    shutil.move(_rar, _savecls)

pause = input("Finalizado!")