## Avaliador
Analisa uma métrica de "Assertividade", verificando se uma classe que possui ao menos uma instância em uma imagem é tem a predição de ao menos uma instância pelo modelo. Possibilita análise de falsos positivos e o salvamento dos resultados.

### Instalação

### Windows
```bash
python -m virtualenv venv
.\venv\Scripts\activate
pip install pyaml
```

### Linux
```bash
python3 -m virtualenv venv
source ./venv/bin/activate
pip install pyaml
```

### Utilização

#### Linux
```bash
source venv/bin/activate
python Avaliador/image_assertivity.py <caminho da pasta de arquivos de labels groundtruth> <caminho da pasta de arquivos de labels preditas> --yaml_path <caminho do arquivo .yaml do dataset> --check_fp <True ou False, analise de falsos positivos> --save <True ou False, salva resultados>
```
#### Windows
```bash
.\venv\Scripts\activate
python.exe Avaliador\image_assertivity.py <caminho da pasta de arquivos de labels groundtruth> <caminho da pasta de arquivos de labels preditas> --yaml_path <caminho do arquivo .yaml do dataset> --check_fp <True ou False, analise de falsos positivos> --save <True ou False, salva resultados>
```


