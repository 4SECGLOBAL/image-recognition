import os, time, bs4,random, requests, shutil
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options 
import pyautogui


from selenium.webdriver.chrome.service import Service as ChromeService


## FUNÇÕES
def pgn_baixo(drive):
    sleep(random.uniform(0.05, 1))
    drive.execute_script("window.scrollTo(0, document.body.scrollHeight);")

## PATHS
_cwd = os.getcwd()
#_chrome = os.path.join(_cwd,"chromedriver.exe")
_save = "Classes"
if not os.path.isdir(_save):
    os.makedirs(_save)
_Downloads = os.path.join(_cwd, "Downloads")
if not os.path.isdir(_Downloads):
    os.makedirs(_Downloads)
_Txts = os.path.join(_cwd, "Txt_Files")
if not os.path.isdir(_Txts):
    os.makedirs(_Txts)

## OPTIONS
options = Options()

options.add_argument(
        "user-data-dir={}\data\chrome_extentions\profile".format(_cwd))
options.add_argument("--profile-directory=test")
options.add_extension('Download-All-Images.crx')


key_run_one_time = 0
xclick = 1170


##
##
##  MAIN
##
##

projeto = input("Qual o nome do projeto?\n")
_projeto = os.path.join(_save,projeto)
if not os.path.isdir(_projeto):
    os.makedirs(_projeto)

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

max_pgn = int(input("Quantas pgns no maximo: "))

antigo_tamanho_downloads = len(os.listdir(_Downloads))
tamanho_atual_downloads = antigo_tamanho_downloads

#começo do scrapping

#driver = ChromeDriverManager().install()
driver = webdriver.Chrome(options=options)
#driver = webdriver.Chrome(options=options)
#driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.get("https://www.google.com")
driver.maximize_window()
sleep(1)
driver.switch_to.window(driver.window_handles[1])
driver.close()
driver.switch_to.window(driver.window_handles[0])
sleep(1)

for q in query_lista:  
    url_ = "https://www.google.com/search?q={}&hl=pt-BR&source=lnms&tbm=isch".format(q.replace(' ','+'))
    #url_ = "https://www.reddit.com/r/trees/"
    sleep(random.uniform(0.5, 2.5))
    driver.get(url_)
    for i in range(0,max_pgn):
        pgn_baixo(driver)
    sleep(random.uniform(1, 1.5))
    driver.execute_script("window.scrollTo(0, 0);")
    if(key_run_one_time == 1):
        xclick = 1150
    key_run_one_time = 1
    pyautogui.click(xclick,y=52,clicks=1,interval=0.0,button="left")
    
    while (antigo_tamanho_downloads == tamanho_atual_downloads):
         sleep(random.uniform(0.5, 1.5))
         tamanho_atual_downloads = len(os.listdir(_Downloads))
    antigo_tamanho_downloads = tamanho_atual_downloads
    
sleep(2)

print("FINALIZADO OS QUERIES")
pause = input("Aperte enter para começar a mover as imagens para a pasta de projeto...")
driver.quit()

for rar in os.listdir(_Downloads):
     _rar = os.path.join(_Downloads,rar)
     _savecls = os.path.join(_projeto,rar)
     shutil.move(_rar, _savecls)

pause = input("Finalizado!")

