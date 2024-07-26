import biblioteca_vis.Utils.Geral

##CLASSE DE IMAGEM COM LABELS ACLOPADO
class vis_Imagem_Labels:

    def __init__(self, nome, lista_de_BBs, MODO_WH_ou_XY = "WH"):
        self.nome = nome
        self.lista_de_BBs = lista_de_BBs
        self.modo = MODO_WH_ou_XY
        self.tamanho_imagem = 0

    def __str__(self):
        return f"(Nome: {self.nome}, Qntd. de BBs: {len(self.lista_de_BBs)}, Modo: {self.modo})"
        
    def transformar_padrão_labels(self, MODO_A_TRANSFORMAR_WH_ou_XY = "WH"):
        if self.modo == MODO_A_TRANSFORMAR_WH_ou_XY:
            raise Exception("Tentativa de transformar um padrão no mesmo padrão")
        elif (self.modo != "WH") and (self.modo != "XY"):
            raise Exception("Erro, padrão a ser transformado não existe (fora de WH ou XY)")
        
        lista_BB_transformada = []
        
        if MODO_A_TRANSFORMAR_WH_ou_XY == "WH":
            for BB in self.lista_de_BBs:
                BB_transformada = BB
                BB_transformada[1:] = Utils.Geral.xy2wh(BB[1], BB[2], BB[3], BB[4])
                lista_BB_transformada.append(BB_transformada)

        elif MODO_A_TRANSFORMAR_WH_ou_XY == "XY":
            for BB in self.lista_de_BBs:
                BB_transformada = BB
                BB_transformada[1:] = Utils.Geral.wh2xy(BB[1], BB[2], BB[3], BB[4])
                lista_BB_transformada.append(BB_transformada)

        novaClasse = vis_Imagem_Labels(self.nome, lista_BB_transformada, MODO_WH_ou_XY=MODO_A_TRANSFORMAR_WH_ou_XY)
        return novaClasse



