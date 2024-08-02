## Requirements

Para utilizar esse software, você deve utilizar have Python 3.8 ou superior. Utiliza-se ambientes virtuais de Python para evitar conflito de dependencias no sistema. Instalar *virtualenv* com:

```bash
pip install virtualenv
```

Dependencias podem ser instaladas da seguinte maneira:

### Windows
```bash
python -m virtualenv venv
.\venv\Scripts\activate
pip install -r .\google-images-download\requirements.txt
```

### Linux
```bash
python3 -m virtualenv venv
source ./venv/bin/activate
pip install -r ./google-images-download/requirements.txt
```

Os `requirements.txt` derivam da ferramenta [google-images-download](https://github.com/ultralytics/google-images-download/blob/main/requirements.txt).

## Como utilizar

Para utilizar o DataScrapper, deve-se seguir os seguintes passos:

1. Garanta que o Google Chrome está instalado na sua máquina. Se não estiver, instale [daqui](https://www.google.com/chrome/).

2. Faça o download do chromedriver correspondente à versão do seu Chrome e do seu sistema operacional (disponível [aqui](https://chromedriver.chromium.org/)) e o coloque neste diretório.

3. Execute o script determinando o caminho do arquivo de texto com os termos de busca desejados e o limite de imagens para download:

### Windows

```
.\execute.bat .\lista_chaves\Arma.txt 50
```

### Linux

```
./execute.sh ./lista_chaves/Arma.txt 50
```

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
python bing_scraper.py --search 'honeybees on flowers' --limit 10 --download --chromedriver .\chromedriver.exe
```

#### Linux
Exemplo para uma única URL:

```bash
source /venv/bin/activate
python bing_scraper.py --url 'https://www.bing.com/images/search?q=flowers' --limit 10 --download --chromedriver ./chromedriver
```

Exemplo para um único termo de busca:

```bash
source /venv/bin/activate
$ python bing_scraper.py --search 'honeybees on flowers' --limit 10 --download --chromedriver ../chromedriver
```

## 📜 Citing the Project

To acknowledge the use of this software in your works, please reference the original repository, which can be found [here](https://github.com/hardikvasa/google-images-download).
## 📋 Requirements

To use this software, ensure you have Python 3.8 or later and all the necessary dependencies installed. Dependencies can be installed by running the following command in your terminal:

```bash
$ pip install -r requirements.txt
```

The `requirements.txt` file is located [here](https://github.com/ultralytics/google-images-download/blob/main/requirements.txt), which includes `selenium` among others.

## ⚙️ Installation

To set up the image scraper on your machine, clone this repository and install the dependencies as shown below:

```bash
$ git clone https://github.com/ultralytics/google-images-download
$ cd google-images-download
$ pip install -r requirements.txt
```

## 🖥️ How to Run

Run the image scraper following these steps:

1. Ensure Google Chrome is installed on your machine. If not, download and install from [here](https://www.google.com/chrome/).

2. Download and update chromedriver corresponding to your version of Chrome [here](https://chromedriver.chromium.org/).

3. Execute the script. Use the `--url` parameter to download images from a specific Bing URL or the `--search` parameter for Bing search terms. By default, the images will be saved in the `./images` directory. Note that any images that cause errors will be skipped during the download process.

Example usage to download images using a URL:

```bash
$ python3 bing_scraper.py --url 'https://www.bing.com/images/search?q=flowers' --limit 10 --download --chromedriver /path/to/your/chromedriver
```

Example usage to download images using search terms:

```bash
$ python3 bing_scraper.py --search 'honeybees on flowers' --limit 10 --download --chromedriver /path/to/your/chromedriver

# Expect output logs showing the download process and any errors encountered.
```
## 📜 Citing the Project

To acknowledge the use of this software in your works, please reference the original repository, which can be found [here](https://github.com/hardikvasa/google-images-download).