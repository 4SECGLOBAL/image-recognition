#  Biblioteca
Biblioteca de funções usadas para manusear o dataset para o projeto

#  Como instalar a biblioteca
Para instalar a biblioteca, baixe o arquivo .whl encontrado na pasta dist do projeto.
Uma vez baixado, mova o arquivo para um diretorio que possa ser acessado pelo terminal.
Com o terminal aberto, instale o arquivo atraves do PIP com o codigo:
"pip install /path/to/wheelfile.whl"
Em seguida é so importar no script de python desejado atraves do comando:
"import biblioteca_vis"

#  Como remontar o arquivo .whl
Para futuras modificações\atualizações do projeto,deve-se usar o codigo:
"python setup.py bdist_wheel"
para atualizações, lembrar de mudar o setup.py e elevar a versão
ex: versão atual = 0.1.0 ; versão update 1 = 0.1.1

#  Ferramentas

- RemoveDuplicata.py: remove imagens duplicadas em um diretorio