Como Utilizar `generate_search_terms()`

A função `generate_search_terms()` é responsável por gerar termos de busca com base em um grafo semântico construído a partir de classes, contextos e sinônimos.

## Estrutura Geral

O grafo é composto por **nós (classes)** e **arestas (contextos entre classes)**. Sinônimos podem ser definidos para cada classe, ampliando a geração de combinações de termos.

## Como Funciona?

A definição de conexões, ou arestas (que podem incluir contextos), entre 2 classes e a definição de contextos e sinônimos para as classes implica que serão gerados, para uma classe, um número de termos correspondente ao número de conexões com outras classes, vezes o número de contextos para cada conexão vezes o número de sinônimos.

### Definindo as Classes

As classes são os elementos centrais do grafo. São definidas como uma lista de strings:

```python
lista_classes = [
    "arma", "faca", "municao", "dinheiro",
    "maconha", "cartao", "documento", "boleto", "print"
]
```

Essas classes são instanciadas em um grafo via:

```python
grafo = GrafoDeClasses(lista_classes)
```

### Definindo Conexões

A definição de uma conexão entre duas classes implica que o par de classes irá gerar um termo de busca que contenha ambas. A definição dessa conexão permite a definição de contextos nos quais ambas as classes devem aparecer juntas e é feito a partir de:

```python
grafo.define_contexto("arma", "municao", [
    "trafico", "traficantes", "crime", "roubo",
    "assalto", "apreendido", "policia", "milicia"
])
```
Cada contexto será combinado com os nomes e sinônimos das classes envolvidas.

### Definindo Sinônimos

Sinônimos expandem as possibilidades de termos gerados. São definidos com:

```python
grafo.define_sinonimos("arma", ["revolver", "pistola"])
```
Isso faz com que as combinações envolvam não apenas "arma", mas também seus sinônimos.

### Gerando os termos
Por fim, os termos são gerados com:

```python
grafo.escreve_termos()
```

Que irá imprimir no terminal algo como:

```
arma e municao trafico
revolver e municao roubo
pistola e municao assalto
...
```

Que deve ser copiado e colado em um arquivo .txt neste diretório. O acesso aos termos será feito pelo DataScrapper a partir do nome do arquivo .txt.
