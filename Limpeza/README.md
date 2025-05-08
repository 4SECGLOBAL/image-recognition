# Limpeza de Dataset

Este repositório contém o script `limpeza_dataset.py`, que realiza a limpeza e preparação de datasets para projetos de reconhecimento de imagens.

## Funcionalidades

- Remove imagens duplicadas ou fora de especificações.
- Métodos de hash simples e perceptual hash (pHash) com embeddings visuais.

## Como usar

### Windows

1. Certifique-se de que o Python 3 está instalado no seu sistema. Você pode baixá-lo em [python.org](https://www.python.org/).
2. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute o script apontando para o diretório do dataset:
    ```bash
    python limpeza_dataset.py C:\caminho\para\dataset --min_largura [min_largura] --min_altura [min_altura] --max_largura [max_largura] --max_altura [max_altura] --limpeza_visual
    ```

### Linux

1. Certifique-se de que o Python 3 está instalado no seu sistema. Você pode instalá-lo usando o gerenciador de pacotes da sua distribuição, como `apt` ou `yum`.
2. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute o script apontando para o diretório do dataset:
    ```bash
    python limpeza_dataset.py /caminho/para/dataset --min_largura [min_largura] --min_altura [min_altura] --max_largura [max_largura] --max_altura [max_altura] --limpeza_visual
    ```

## Parâmetros

- **min_largura, min_altura**: dimensões mínimas (padrão: 100x100)
- **max_largura, max_altura**: dimensões máximas (padrão: 1920x1080)
- *--limpeza_visual*: usa pHash + embeddings visuais (opcional)