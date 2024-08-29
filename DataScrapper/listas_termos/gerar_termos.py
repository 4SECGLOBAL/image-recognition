
class NoDeClasse():
    def __init__ (self, numero, nome):
        self.numero = numero
        self.nome = nome
        self.lista_sinonimos = []
    def define_sinonimos(self, lista_sinonimos):
        self.lista_sinonimos = lista_sinonimos

class ArestaDeContexto():
    def __init__ (self, noA, noB, lista_contextos):
        self.noA = noA
        self.noB = noB
        self.lista_contextos = lista_contextos
    def set_lista_contextos(self, lista_contextos):
        self.lista_contextos = lista_contextos
    def define_sinonimos(self, lista_sinonimos, no):
        if no == self.noA.numero:
            self.noA.define_sinonimos(lista_sinonimos)
        else:
            self.noB.define_sinonimos(lista_sinonimos)

class GrafoDeClasses():
    def __init__ (self, n_classes, lista_classes):

        self.n_classes = n_classes
        self.lista_nos = []
        self.dict_classes = {}
        for i in range(n_classes):
            self.lista_nos.append(NoDeClasse(i, lista_classes[i]))
            self.dict_classes[lista_classes[i]] = i

        self.matriz_adj = []
        for i in range(n_classes):
            row = []
            for j in range(0, n_classes):
                noA = self.lista_nos[i]
                noB = self.lista_nos[j]
                row.append(ArestaDeContexto(noA, noB, None))
            self.matriz_adj.append(row)
            
    def define_contexto(self, nome_noA, nome_noB, lista_contextos):
        noA = self.dict_classes[nome_noA]
        noB = self.dict_classes[nome_noB]
        self.matriz_adj[noA][noB].set_lista_contextos(lista_contextos)

    def define_sinonimos(self, nome_no, lista_sinonimos):
        no = self.dict_classes[nome_no]
        for i in range(self.n_classes):
            self.matriz_adj[no][i].define_sinonimos(lista_sinonimos, no)

    def escreve_termos(self):
        for i in range(self.n_classes):
            for j in range(i, self.n_classes):
                aresta = self.matriz_adj[i][j]
                if i != j:
                    print(aresta.noA.nome + " e " + aresta.noB.nome)
                    self.escreve_termos_contextos(aresta, aresta.noA.nome, aresta.noB.nome)
                    for sinonimo in aresta.noA.lista_sinonimos:
                        self.escreve_termos_contextos(aresta, sinonimo, aresta.noB.nome)
                    for sinonimo in aresta.noB.lista_sinonimos:
                        self.escreve_termos_contextos(aresta, aresta.noA.nome, sinonimo)
                
    def escreve_termos_contextos(self, aresta, termoA, termoB):
        if aresta.lista_contextos is not None:
                for contexto in aresta.lista_contextos:
                        print(termoA + " e " + termoB + " " + contexto)
                

def generate_search_terms():
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
    
    
    grafo = GrafoDeClasses(9, lista_classes)

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

    grafo.define_sinonimos("arma", ["revolver", "pistola"])

    grafo.escreve_termos()

generate_search_terms()