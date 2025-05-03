# DataScrapper

Essa ferramenta permite fazer o download de um número determinado de imagens da web a partir de termos de busca avulsos ou, principalmente, listados em arquivos .txt. Utiliza como submódulo o repositório mantido pela [Ultralytics](https://github.com/ultralytics/google-images-download), que é baseado no trabalho de [hardikvasa](https://github.com/hardikvasa/google-images-download).

## Requirements

Para utilizar esse software, você deve utilizar Python 3.8 ou superior. Utiliza-se ambientes virtuais de Python para evitar conflito de dependencias no sistema. Instalar *virtualenv* com:

```bash
pip install virtualenv
```

Dependencias podem ser instaladas da seguinte maneira:

### Windows
```bash
# Atualizar os arquivos do repositório google-images-download
git pull --recurse-submodules
# Instalar os requirements de python
python -m virtualenv venv
.\venv\Scripts\activate
pip install -r .\google-images-download\requirements.txt
```

### Linux
```bash
# Atualizar os arquivos do repositório google-images-download
git pull --recurse-submodules
# Instalar os requirements de python
python3 -m virtualenv venv
source ./venv/bin/activate
pip install -r ./google-images-download/requirements.txt
```

Os `requirements.txt` derivam da ferramenta [google-images-download](https://github.com/ultralytics/google-images-download/blob/main/requirements.txt).

## Como utilizar

Para utilizar o DataScrapper, deve-se seguir os seguintes passos:

1. Garanta que o Google Chrome está instalado na sua máquina. Se não estiver, instale [daqui](https://www.google.com/chrome/).

2. Faça o download do chromedriver correspondente à versão do seu Chrome e do seu sistema operacional (disponível [aqui](https://chromedriver.chromium.org/)) e, para Windows, o coloque neste diretório, e para Linux o coloque em /usr/local/bin/.

3. Execute o script determinando o nome do arquivo de texto com os termos de busca desejados (presentes na pasta ./listas_termos/) e o limite de imagens para download, nessa ordem, e as imagens serão baixadas em `./images/<termo de busca>`. O argumento `-join` é opcional e resulta em uma pasta com todas as imagens resultantes do arquivo de termos no mesmo diretório, caso não utilizada, as imagens são separadas em pastas nomeadas pelo termo da busca utilizada:

#### Windows

```
.\execute.bat Arma 50 -join
```

#### Linux

```
./execute.sh Arma 50 -join
```

**OBS**: ``-join`` é opcional

### Adicionar arquivos de termos de busca
Para utilizar novas listagens de termos de busca, basta criar um novo arquivo .txt na pasta `./listas_termos` com cada termo de busca presente em uma nova linha do arquivo. Como por exemplo:
```
termo de busca 1
termo de busca 2
termo de busca 3
```

**OBS**: o script *gerar_termos.py* possibilita a geração de uma combinação de duplas de classes associadas com contextos e sinônimos, acesse `./listas_termos/README.md` para mais informações sobre como utilizá-lo.

### Termo de busca único

É possível realizar uma busca de um único termo, utilizando uma url ou termo de busca, com regulagem de número de imagens limite para fazer download:

#### Windows
Exemplo para uma única URL:

```bash
.\venv\Scripts\activate
python bing_scraper.py --url 'https://www.bing.com/images/search?q=flowers' --limit 10 --download --chromedriver .\chromedriver.exe
```

Exemplo para um único termo de busca:

```bash
.\venv\Scripts\activate
python bing_scraper.py --search 'honeybees on flowers' --limit 10 --download --chromedriver .\chromedriver\chromedriver.exe
```

#### Linux
Exemplo para uma única URL:

```bash
source /venv/bin/activate
python bing_scraper.py --url 'https://www.bing.com/images/search?q=flowers' --limit 10 --download --chromedriver /usr/local/bin/chromedriver
```

Exemplo para um único termo de busca:

```bash
source /venv/bin/activate
$ python bing_scraper.py --search 'honeybees on flowers' --limit 10 --download --chromedriver /usr/local/bin/chromedriver
```
