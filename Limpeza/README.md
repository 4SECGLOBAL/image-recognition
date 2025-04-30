# Limpeza de Dataset

Este repositório contém o script `limpeza_dataset.py`, que realiza a limpeza e preparação de datasets para projetos de reconhecimento de imagens.

## Funcionalidades

- Remoção de arquivos corrompidos ou inválidos.
- Organização de imagens em diretórios específicos.
- Renomeação de arquivos para um padrão consistente.
- Exclusão de duplicatas com base em hashes e pHashes.

## Como usar

### Windows

1. Certifique-se de que o Python 3 está instalado no seu sistema. Você pode baixá-lo em [python.org](https://www.python.org/).
2. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute o script apontando para o diretório do dataset:
    ```bash
    python limpeza_dataset.py --input_dir C:\caminho\para\dataset --output_dir C:\caminho\para\saida
    ```

### Linux

1. Certifique-se de que o Python 3 está instalado no seu sistema. Você pode instalá-lo usando o gerenciador de pacotes da sua distribuição, como `apt` ou `yum`.
2. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```
3. Execute o script apontando para o diretório do dataset:
    ```bash
    python limpeza_dataset.py --input_dir /caminho/para/dataset --output_dir /caminho/para/saida
    ```

## Parâmetros

- `--input_dir`: Diretório contendo o dataset original.
- `--output_dir`: Diretório onde o dataset limpo será salvo.
- `--remove_duplicates`: (Opcional) Remove arquivos duplicados.
- `--log_file`: (Opcional) Caminho para salvar o log do processo.
