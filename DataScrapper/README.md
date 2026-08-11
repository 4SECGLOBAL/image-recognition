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

## Preparar o dataset COCO 2017

O script `coco_class.py` baixa o COCO 2017 e organiza suas imagens e anotações
de detecção no formato esperado pelo Ultralytics YOLO. Ele apenas prepara o
dataset; o treinamento do modelo deve ser executado separadamente.

Execute os comandos abaixo a partir da raiz do repositório. Além do ambiente
virtual descrito acima, instale as dependências usadas pelo script:

```bash
pip install requests PyYAML tqdm ultralytics
```

O pacote `tqdm` é opcional e serve somente para exibir a barra de progresso. O
pacote `ultralytics` é necessário para baixar o dataset completo; no modo
limitado, o script usa diretamente `requests` e `PyYAML`.

### Baixar o COCO completo

```bash
python DataScrapper/coco_class.py
```

Por padrão, o dataset é salvo em `DataScrapper/datasets/coco`, com os splits
`train2017` e `val2017`. Esse modo verifica se há pelo menos 45 GiB livres e,
ao final, valida a presença das 118.287 imagens de treino e 5.000 imagens de
validação.

Para incluir também o split público de teste, que não possui anotações
públicas:

```bash
python DataScrapper/coco_class.py --include-test
```

Para salvar em outro disco ou diretório:

```bash
python DataScrapper/coco_class.py --dataset-dir /caminho/para/coco
```

### Baixar uma amostra limitada

Use `--limit` para baixar somente uma amostra estratificada entre as 80 classes
do COCO. O total informado é dividido em aproximadamente 90% para treino e 10%
para validação:

```bash
python DataScrapper/coco_class.py --limit 20000
```

Quando `--dataset-dir` não é informado, esse modo salva os dados em
`DataScrapper/datasets/coco20k`. O limite mínimo é de 80 imagens. O script baixa
as anotações oficiais, seleciona as imagens, converte as bounding boxes para o
formato YOLO e cria `coco20k.yaml`, que pode ser usado no treinamento:

```bash
yolo detect train data=DataScrapper/datasets/coco20k/coco20k.yaml model=yolo11n.pt
```

É possível controlar a repetibilidade da seleção e a quantidade de downloads
simultâneos:

```bash
python DataScrapper/coco_class.py \
  --limit 5000 \
  --seed 123 \
  --workers 16 \
  --dataset-dir DataScrapper/datasets/coco5k
```

Os argumentos disponíveis são:

- `--dataset-dir`: diretório de destino;
- `--include-test`: inclui `test2017` no download completo (é ignorado no modo
  limitado);
- `--limit`: ativa o modo limitado e define o total de imagens;
- `--seed`: semente da seleção estratificada (padrão: `42`);
- `--workers`: número de downloads simultâneos no modo limitado (padrão: `8`).

Downloads já concluídos são reaproveitados. Se uma transferência falhar,
execute novamente o mesmo comando para tentar completar o dataset.

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

### API para coleta e limpeza

```text
POST http://localhost:8001/api/1/datascrapper/coleta-e-limpeza?termo_busca=cedula%20de%2020%20reais%0Anota%20de%2050%20reais%0Adinheiro%20brasileiro
```

`termo_busca` e um parametro obrigatorio do endpoint, fora do body. Cada linha nao vazia ou trecho separado por `;` vira um termo de busca independente. O body fica somente com as configuracoes da coleta:

```json
{
  "limite": 80,
  "min_larg": 200,
  "min_alt": 200,
  "max_larg": 1280,
  "max_alt": 720,
  "limpeza": true,
  "limpeza_visual": true,
  "anonimo": false
}
```

A resposta inclui `termos_submetidos`, com a lista normalizada dos termos que foram enviados para coleta.

### API para gerar termos

A API tambem pode gerar um arquivo de termos a partir de uma lista de classes:

```text
POST http://localhost:8001/api/1/datascrapper/gerar_termos
```

Exemplo de payload:

```json
{
  "classes": "dinheiro, arma, faca, municao, drogas, cartao, documento, boleto, print"
}
```

O endpoint cria `DataScrapper/listas_termos/Classes_e_contextos_<datahoje>.txt`
e retorna o conteudo gerado no campo `conteudo`.

### API para augmentation de tonalidades

```text
POST http://localhost:8001/api/1/datascrapper/augment-tonalidades
```

O endpoint gera as seguintes transformacoes:

1. `cinza`
2. `amarelado`
3. `azulado`
4. `esverdeada`
5. `infravermelho`
6. `claro`
7. `escuro`
8. `muito_escuro`
9. `contraste_alto`
10. `contraste_baixo`
11. `desfocado`
12. `compressao_jpeg`
13. `cftv_noite`
14. `rot90`
15. `rot180`
16. `rot270`
17. `espelhada`

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
