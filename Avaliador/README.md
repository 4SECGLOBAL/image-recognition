## Avaliador

### API de avaliação

O serviço `evaluator-api`, exposto na porta `8003` pelo Compose, executa a
avaliação completa no conjunto `test`:

```text
POST http://localhost:8003/api/3/evaluator/evaluate
```

Exemplo de payload:

```json
{
  "data": "Avaliador/data.yaml",
  "model": "runs/detect/train-27/weights/best.pt",
  "test_path": "Avaliador/test",
  "confidence": 0.25,
  "device": "0",
  "save_json": true
}
```

Os campos `confidence`, `device` e `save_json` são opcionais. Os gráficos e a
matriz de confusão produzidos pelo YOLO são armazenados em
`Avaliador/validacao/`.

O campo `model` também pode ser omitido. Nesse caso, a API localiza em tempo de
execução o `weights/best.pt` do treinamento mais recente em `runs/detect`.

A resposta informa:

- `validation_dir`: caminho relativo `Avaliador/validacao`;
- `validation_dir_absoluto`: caminho da pasta dentro do container;
- `artefatos_gerados`: todos os arquivos criados ou atualizados pela execução;
- `matriz_confusao`: caminho de `confusion_matrix.png`;
- `matriz_confusao_normalizada`: caminho de `confusion_matrix_normalized.png`;
- `matriz_confusao_xlsx`: caminho de `confusion_matrix.xlsx`, com os valores absolutos;
- `assertivity_file`: caminho do relatório `assertivity.txt`.
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
