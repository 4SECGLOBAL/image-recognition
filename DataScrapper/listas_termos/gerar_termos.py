import re


CONTEXTOS_PADRAO = {
    frozenset(("arma", "municao")): ["trafico", "traficantes", "crime", "roubo", "assalto", "apreendido", "policia", "milicia"],
    frozenset(("arma", "faca")): ["homem segurando", "pessoa segurando", "apreendido", "policia"],
    frozenset(("arma", "drogas")): ["trafico", "traficantes", "crime", "apreendido", "policia", "milicia"],
    frozenset(("arma", "maconha")): ["homem segurando", "pessoa segurando", "trafico", "traficantes", "crime", "apreendido", "policia"],
    frozenset(("arma", "dinheiro")): ["homem segurando", "pessoa segurando", "apreendido", "policia"],
    frozenset(("municao", "drogas")): ["trafico", "traficantes", "crime", "apreendido", "policia", "milicia"],
    frozenset(("municao", "maconha")): ["trafico", "traficantes", "crime", "apreendido", "policia", "milicia"],
    frozenset(("dinheiro", "drogas")): ["trafico", "traficantes", "crime", "apreendido", "policia", "milicia"],
    frozenset(("dinheiro", "maconha")): ["trafico", "traficantes", "crime", "apreendido", "policia", "milicia"],
    frozenset(("dinheiro", "cartao")): ["na mesa", "apreendido", "policia"],
    frozenset(("dinheiro", "boleto")): ["na mesa"],
    frozenset(("dinheiro", "documento")): ["na mesa", "policia"],
    frozenset(("cartao", "documento")): ["na mesa"],
    frozenset(("cartao", "boleto")): ["na mesa"],
    frozenset(("documento", "boleto")): ["na mesa"],
    frozenset(("print", "documento")): ["na tela"],
    frozenset(("print", "boleto")): ["na tela"],
    frozenset(("print", "cartao")): ["na tela"],
    frozenset(("dinheiro", "celular")): ["na mesa", "apreendido", "policia"],
    frozenset(("arma", "celular")): ["apreendido", "policia", "roubo", "assalto"],
    frozenset(("faca", "celular")): ["apreendido", "policia", "roubo", "assalto"],
    frozenset(("municao", "celular")): ["apreendido", "policia"],
    frozenset(("drogas", "celular")): ["trafico", "traficantes", "crime", "apreendido", "policia"],
    frozenset(("cartao", "celular")): ["na mesa"],
    frozenset(("documento", "celular")): ["na mesa"],
    frozenset(("boleto", "celular")): ["na tela"],
    frozenset(("print", "celular")): ["na tela"],
}
SINONIMOS_PADRAO = {
    "arma": ["revolver", "pistola"],
    "drogas": ["maconha", "entorpecentes"],
}


def normalizar_lista_classes(value: str) -> list[str]:
    classes = []
    vistos = set()
    for classe in re.split(r"[,\n]+", value):
        classe_normalizada = re.sub(r"\s+", " ", classe.strip().lower())
        if not classe_normalizada or classe_normalizada in vistos:
            continue
        if not re.fullmatch(r"[\wÀ-ÿ -]+", classe_normalizada):
            raise ValueError("Use apenas letras, numeros, espacos, hifen e underline nas classes.")
        classes.append(classe_normalizada)
        vistos.add(classe_normalizada)
    return classes


class GeradorTermosBusca:
    def __init__(self, contextos=None, sinonimos=None):
        self.contextos = contextos or CONTEXTOS_PADRAO
        self.sinonimos = sinonimos or SINONIMOS_PADRAO

    def gerar(self, classes: str | list[str]) -> list[str]:
        classes_normalizadas = self.normalizar_classes(classes)
        termos = []
        vistos = set()

        for indice_a, classe_a in enumerate(classes_normalizadas):
            for classe_b in classes_normalizadas[indice_a + 1 :]:
                contextos = self.contextos.get(frozenset((classe_a, classe_b)), [])
                pares = [(classe_a, classe_b)]

                for sinonimo in self.sinonimos.get(classe_a, []):
                    pares.append((sinonimo, classe_b))
                for sinonimo in self.sinonimos.get(classe_b, []):
                    pares.append((classe_a, sinonimo))

                for termo_a, termo_b in pares:
                    self._adicionar_termo(termos, vistos, f"{termo_a} e {termo_b}")
                    for contexto in contextos:
                        self._adicionar_termo(termos, vistos, f"{termo_a} e {termo_b} {contexto}")

        return termos

    def normalizar_classes(self, classes: str | list[str]) -> list[str]:
        if isinstance(classes, str):
            return normalizar_lista_classes(classes)
        return normalizar_lista_classes(",".join(classes))

    def gerar_classes_e_sinonimos(self, classes: str | list[str]) -> dict[str, list[str]]:
        return {classe: self.sinonimos.get(classe, []) for classe in self.normalizar_classes(classes)}

    def gerar_correlacoes_entre_classes(self, classes: str | list[str]) -> list[dict[str, object]]:
        classes_normalizadas = self.normalizar_classes(classes)
        correlacoes = []
        for indice_a, classe_a in enumerate(classes_normalizadas):
            for classe_b in classes_normalizadas[indice_a + 1 :]:
                correlacoes.append(
                    {
                        "classe_a": classe_a,
                        "classe_b": classe_b,
                        "contextos": self.contextos.get(frozenset((classe_a, classe_b)), []),
                    }
                )
        return correlacoes

    def gerar_conteudo(self, classes: str | list[str], delimitador: str = ";") -> str:
        linhas = ["# Classes e sinônimos"]

        for classe, sinonimos in self.gerar_classes_e_sinonimos(classes).items():
            if sinonimos:
                linhas.append(f"{classe}: {', '.join(sinonimos)}")
            else:
                linhas.append(classe)

        linhas.extend(["", "# Correlações entre classes"])
        for correlacao in self.gerar_correlacoes_entre_classes(classes):
            contextos = correlacao["contextos"]
            linha = f"{correlacao['classe_a']} + {correlacao['classe_b']}"
            if contextos:
                linha += f": {', '.join(contextos)}"
            linhas.append(linha)

        linhas.extend(["", "# Termos de busca", *self.gerar(classes)])
        return "\n".join(f"{linha}{delimitador}" if linha else "" for linha in linhas) + "\n"

    @staticmethod
    def _adicionar_termo(termos: list[str], vistos: set[str], termo: str) -> None:
        termo = re.sub(r"\s+", " ", termo.strip())
        if termo and termo not in vistos:
            termos.append(termo)
            vistos.add(termo)


# Classe que representa um nó no grafo, ou seja, uma classe semântica (ex: "arma", "dinheiro", etc.)
class NoDeClasse():
    def __init__(self, numero, nome):
        self.numero = numero                  # Índice único do nó
        self.nome = nome                      # Nome da classe
        self.lista_sinonimos = []             # Lista de sinônimos associados a esse nó

    def define_sinonimos(self, lista_sinonimos):
        self.lista_sinonimos = lista_sinonimos 


# Classe que representa uma aresta entre dois nós (classes), com contextos semânticos
class ArestaDeContexto():
    def __init__(self, noA, noB, lista_contextos):
        self.noA = noA                        # Primeiro nó
        self.noB = noB                        # Segundo nó
        self.lista_contextos = lista_contextos  # Lista de contextos (palavras relacionadas)

    def set_lista_contextos(self, lista_contextos):
        self.lista_contextos = lista_contextos

    def define_sinonimos(self, lista_sinonimos, no):
        # Aplica os sinônimos no nó correspondente da aresta
        if no == self.noA.numero:
            self.noA.define_sinonimos(lista_sinonimos)
        else:
            self.noB.define_sinonimos(lista_sinonimos)


# Classe principal que representa o grafo das classes semânticas
class GrafoDeClasses():
    def __init__(self, lista_classes):
        self.n_classes = len(lista_classes)    # Número total de classes
        self.lista_nos = []                    # Lista de objetos NoDeClasse
        self.dict_classes = {}                 # Mapeia nome da classe para índice

        # Criação dos nós e mapeamento dos nomes
        for i in range(self.n_classes):
            self.lista_nos.append(NoDeClasse(i, lista_classes[i]))
            self.dict_classes[lista_classes[i]] = i

        # Inicialização da matriz de adjacência com arestas vazias (sem contextos)
        self.matriz_adj = []
        for i in range(self.n_classes):
            row = []
            for j in range(self.n_classes):
                noA = self.lista_nos[i]
                noB = self.lista_nos[j]
                row.append(ArestaDeContexto(noA, noB, None))
            self.matriz_adj.append(row)

    # Define os contextos entre dois nós a partir de seus nomes
    def define_contexto(self, nome_noA, nome_noB, lista_contextos):
        noA = self.dict_classes[nome_noA]
        noB = self.dict_classes[nome_noB]
        self.matriz_adj[noA][noB].set_lista_contextos(lista_contextos)

    # Atribui sinônimos a um nó específico
    def define_sinonimos(self, nome_no, lista_sinonimos):
        no = self.dict_classes[nome_no]
        for i in range(self.n_classes):
            self.matriz_adj[no][i].define_sinonimos(lista_sinonimos, no)

    # Gera e imprime os termos de busca combinando os nomes e sinônimos com os contextos
    def escreve_termos(self):
        for i in range(self.n_classes):
            for j in range(i, self.n_classes):
                aresta = self.matriz_adj[i][j]
                if i != j:
                    print(aresta.noA.nome + " e " + aresta.noB.nome)
                    self.escreve_termos_contextos(aresta, aresta.noA.nome, aresta.noB.nome)

                    # Combina os sinônimos com os contextos
                    for sinonimo in aresta.noA.lista_sinonimos:
                        self.escreve_termos_contextos(aresta, sinonimo, aresta.noB.nome)
                    for sinonimo in aresta.noB.lista_sinonimos:
                        self.escreve_termos_contextos(aresta, aresta.noA.nome, sinonimo)

    # Imprime as combinações entre dois termos usando os contextos definidos
    def escreve_termos_contextos(self, aresta, termoA, termoB):
        if aresta.lista_contextos is not None:
            for contexto in aresta.lista_contextos:
                print(termoA + " e " + termoB + " " + contexto)


# Função principal que cria o grafo, define os contextos, sinônimos e imprime os termos finais
def generate_search_terms():
    # Lista de classes principais que compõem os nós do grafo
    lista_classes = [
        "arma", 
        "faca",
        "municao",
        "dinheiro",
        "maconha",
        "cartao",
        "documento",
        "boleto",
        "print"
    ]

    # Cria o grafo com 9 classes
    grafo = GrafoDeClasses(lista_classes)

    # Define os contextos entre pares de classes
    grafo.define_contexto("arma", "municao", ["trafico", "traficantes", "crime", "roubo", "assalto", "apreendido", "policia", "milicia"])
    grafo.define_contexto("arma", "faca", ["homem segurando", "pessoa segurando"])
    grafo.define_contexto("arma", "maconha", ["homem segurando", "pessoa segurando"])
    grafo.define_contexto("arma", "dinheiro", ["homem segurando", "pessoa segurando"])
    grafo.define_contexto("municao", "maconha", ["trafico", "traficantes", "crime", "apreendido", "policia", "milicia"])
    grafo.define_contexto("dinheiro", "maconha", ["trafico", "traficantes", "crime", "apreendido", "policia", "milicia"])
    grafo.define_contexto("dinheiro", "cartao", ["na mesa", "apreendido", "policia"])
    grafo.define_contexto("dinheiro", "boleto", ["na mesa"])
    grafo.define_contexto("dinheiro", "documento", ["na mesa", "policia"])
    grafo.define_contexto("cartao", "documento", ["na mesa"])
    grafo.define_contexto("cartao", "boleto", ["na mesa"])
    grafo.define_contexto("documento", "boleto", ["na mesa"])
    grafo.define_contexto("print", "print", ["na tela"])

    # Adiciona sinônimos para a classe "arma"
    grafo.define_sinonimos("arma", ["revolver", "pistola"])

    # Gera e imprime os termos de busca baseados nos contextos e sinônimos
    grafo.escreve_termos()

if __name__ == "__main__":
    generate_search_terms()
