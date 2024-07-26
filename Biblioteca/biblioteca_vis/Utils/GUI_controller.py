
from math import ceil
from time import sleep

LINE_UP = '\033[1A'
LINE_DOWN = '\033[1B'
CURSOR_LEFT = '\033[1D'
CURSOR_RIGHT = '\033[1C'
LINE_CLEAR = '\033[2K'

class Controlador_GUI:
    def __init__(self) -> None:
        pass
    
    def titulo(self, Texto, bLargura = 50, bAltura = 5, simb = "@", cTop = True, cBot = True, tempo = 0):
        txt = Texto.split("~")
        Linhas = len(txt)
        tempo = tempo / bAltura
        alturaInicio = int((bAltura - Linhas)/2) + 1
        ai = 1
        ti = 0
        while(ai <= bAltura):
            li = 1
            if (ai == 1 and cTop == True) or (ai == bAltura and cBot == True):
                while (li <= bLargura):
                    print(simb, end = '')
                    li = li+1
                print("")
            elif alturaInicio<=ai<=(alturaInicio+Linhas-1):
                ini = int((bLargura - 2)/2) - int(len(txt[ti])/2)
                print(simb, end = '')
                while(li < (bLargura - len(txt[ti]))):
                    if li == ini:
                        print(txt[ti], end = '')
                    else:
                        print(" ", end = '')
                    li = li+1
                print(simb)
                ti = ti + 1
            else:
                print(simb, end = '')
                while(li < (bLargura - 1)):
                    print(" ", end = '')
                    li = li + 1
                print(simb)
            ai = ai + 1
            sleep(tempo)
        return

    def cursor(self,y = 0, x = 0):
        if(y > 0):
            cmdV = '\033['+str(y)+'A'
            print(cmdV,end='')
        elif(y < 0):
            cmdV = '\033['+str(abs(y))+'B'
            print(cmdV,end='')
        if(x < 0):
            cmdH = '\033['+str(abs(x))+'D'
            print(cmdH,end='')
        elif(x > 0):
            cmdH = '\033['+str(x)+'C'
            print(cmdH,end='')
        return

    def print_devagar(self,texto, tempo = 0, new_line = True):
        tempo = tempo / len(texto)
        for c in texto:
            sleep(tempo)
            print (c,end='')
        if new_line:
            print('')

    def limpar_linhas(self,linhas = 1,tempo = 0):
        tempo = tempo/linhas
        i = 0
        while(i < linhas):
            sleep(tempo)
            print(LINE_UP,end=LINE_CLEAR)
            i = i + 1
            print('')
            print(LINE_UP,end='')
        return

    def limpar_detalhe(self,cInicio, cFinal, fim = 300, tudo = False):
        if tudo:
            print(LINE_CLEAR)
        else:
            i = 1
            while(i < fim):
                if (cInicio<=i<=(cFinal+1)):
                    print(' ',end='')
                else:
                    print(CURSOR_RIGHT,end='')
                i = i + 1
        print('')
        return
      
    def input_com_saida(self, entrada, linha = 0, tempos=0):
        if (entrada == '0') or (entrada.lower() == "sair"):
            self.limpar_linhas(linhas=linha,tempo=tempos)
            exit()
        else:
            return entrada


