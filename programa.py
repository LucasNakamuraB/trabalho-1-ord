import os
import argparse
from struct import pack, unpack, calcsize

primary_format = "ii"
reverse_format = "iii"

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--build', action="store_true", help="Gera novo arquivo de indices")
parser.add_argument('-e', '--execute', metavar='filename', help="Executa o arquivo de comandos")
parser.add_argument('-c', '--compact', action="store_true", help="Compacta o arquivo \"games.dat\"")

args = parser.parse_args()

in_file = open("games.dat", 'rb+')
primario = None
genero = None
publicadora = None
inversa = None

fields = ["id", "nome", "ano", "genero", "publicadora", "plataforma"]

primary_index: list = []
genero_index: list = []
publicadora_index: list = []
lista_inversa: list = []

def main() -> None:
    if args.build:
        print('-- Construindo índice --')
        generate_indexes()
        print('-- Índice construído --')
        
    elif args.execute:
        print("-- Arquivo de instruções: "+ str(args.execute) + ".txt aberto --")
        load_indexes()
        #print(primary_index)
        print(lista_inversa)
        #print(genero_index)
        print(publicadora_index)
        print("-- Instruções concluídas --")
    elif args.compact:
        print("-- Compactando arquivo --")
        print("-- Arquivo compactado --")

#Execução de operações -------------------------------------------------------|

def execute(filename: str) -> None:
    '''
    Recebe o nome de um arquivo de texto e realiza as operações contidas nele
    '''

def interpretate(operat: str):
    '''
    interpreta a operação descrita em *operat* e realiza a função de acordo
    '''
    pass

def id_search(id: int) -> list[str|None]:
    '''
    recebe um *id* de jogo e procura ele no indice primario, existir, retorna
    o registro lido por *read_registry()*, se não, retorna uma lista vazia
    '''

def genero_search(gen: str) -> list:
    '''
    procura na lista secundária de generos os jogos de genero *gen*,
    e retorna uma lista deles, ou lista vazia se o genero for inválido
    '''

def publicadora_search(pub: str) -> list:
    '''
    procura na lista secundária de publicadoras os jogos de publicadora *pub*,
    e retorna uma lista deles, ou lista vazia se a poblucadora for inválida
    '''

def insert(registry: str):
    '''
    Insere o registro em *games.dat*, se o id não for repetido
    '''

def remove(id: int):
    '''
    remove lógicamente o registro de *id* do arquivo, e atualiza os índices 
    '''

#Geração de índices ----------------------------------------------------------| 

def generate_indexes() -> None:
    '''
    Gera os arquívos de índices ou sobrescreve os atuais
    '''
    generate_primary_index()
    genero_index = generate_secondary_index(3)
    publicadora_index = generate_secondary_index(4)
    generate_inversa_file()
    genero = generate_file("genero.ind", genero_index)
    publicadora = generate_file("publicadora.ind", publicadora_index)
    #print(lista_inversa)
    #print(genero_index)
    #print(publicadora_index)

def generate_primary_index() -> None:
    '''
    Gera um arquivo de indices primários ou substitui caso já houver
    '''
    primario = open("primario.ind", "wb+")
    reg = ['buxa']
    while reg != []:
        offset = in_file.seek(0, os.SEEK_CUR)
        reg = read_registry(in_file)
        if reg:
            primary_index.append((int(reg[0]), offset))
    primary_index.sort()
    for idx in primary_index:
        primario.write(pack(primary_format, idx[0], idx[1]))

def generate_secondary_index(field_index: int) -> list[tuple]:
    '''
    Gera um índice secundário do campo de indice *field_index* em *fields*, e
    adiciona ele à lista inversa
    '''
    index_name = fields[field_index] + ".ind"
    sec_ind = open(index_name, "wb")
    secondary = []
    for index in primary_index:
        in_file.seek(index[1])
        reg = read_registry(in_file)
        pos = check_sec_for(secondary, reg[field_index])
        if len(secondary) == 0 or pos == -1:
            i = add_inversa_single(int(reg[0]))
            secondary.append((reg[field_index], i))
        else:
            add_to_inversa(pos,field_index,int(reg[0]))
    secondary.sort()
    
    return secondary

def check_sec_for(lst, campo: str) -> int:
    '''
    verifica se a lista de indices secundarios possui *campo*,
    se possuir, retorna sua posição, se não, retorna -1
    '''
    i = 0
    found = False
    pos = -1
    while i< len(lst) and not found:
        if lst[i][0] == campo:
            found = True
            pos = lst[i][1]
        i += 1
    return pos

def add_to_inversa(pos: int, field: int, id: int) -> None:
    '''
    Percorre o encadeamento contido no campo *field*, atualiza o ultimo item e
    adiciona um item com *id*
    '''
    next = field -2
    item = lista_inversa[pos]
    print(item)
    if item[next] == -1:
        a = add_inversa_single(id)
        new_tup = [item[0], item[1], item[2]]
        new_tup[next] = a
        lista_inversa[pos] = (new_tup[0], new_tup[1], new_tup[2])
    else:
        add_to_inversa(item[next], next + 2, id)

def add_inversa_single(id: int) -> int:
    '''
    Usado caso um item seja o primeiro de seu indice secundario,
    procura um item de mesmo *id*, o atualiza e retorna sua posição, se nao,
    adiciona ao fim da lista
    '''
    i = 0
    found = False
    while not found and i < len(lista_inversa):
        item = lista_inversa[i]
        if item[0] == id:
            found = True
            tup_form = (id, item[1], item[2])
            lista_inversa[i] = tup_form
        i += 1
    if not found:
        lista_inversa.append((id, -1, -1))
        return len(lista_inversa) -1
    if found:
        return i -1

#Geração de arquivos ---------------------------------------------------------|

def generate_file(name: str, lst: list):
    '''
    Escreve os campos de *lst* para um arquivo de nome *name* usando a função
    *write_field()* e retorna ele
    '''   
    file = open(name, 'wb')
    for index in lst:
        write_regstry(file, index)
    return file

def generate_inversa_file():
    '''
    gera um arquivo binario com base na *lista_inversa*
    '''
    inversa = open("inversa.lst", "wb")
    for i in lista_inversa:
        idx_bytes = pack(reverse_format, i[0], i[1], i[2])
        inversa.write(idx_bytes)

#Carregamento de índices -----------------------------------------------------|

def load_indexes() -> None:
    '''
    carrega os arquivos de indice em suas respectivas listas
    '''
    primary_index = load_primary_index()
    lista_inversa = load_inversa()
    genero = open("genero.ind", 'rb')
    publicadora = open("publicadora.ind", 'rb')
    load_secundaria(genero, genero_index)
    load_secundaria(publicadora, publicadora_index)

def load_primary_index() -> None:
    '''
    carrega o arquivo *primario.ind* em uma *primary_index* em formato 
    *(indice, byte-offset)* 
    '''
    primario =  open("primario.ind", "rb")
    idx_bytes = primario.read(calcsize(primary_format))
    while idx_bytes:
        idx = unpack(primary_format, idx_bytes)
        primary_index.append(idx)
        idx_bytes = primario.read(calcsize(primary_format))

def load_inversa() -> None:
    '''
    Retorna uma lista contendo os indices da lista inversa na forma de tuplas
    '''
    inversa =  open("inversa.lst", "rb")
    idx_bytes = inversa.read(calcsize(reverse_format))
    while idx_bytes:
        idx = unpack(reverse_format, idx_bytes)
        lista_inversa.append(idx)
        idx_bytes = inversa.read(calcsize(reverse_format))
      
def load_secundaria(file, lst: list):
    '''
    Retorna uma lista contendo os indices de um indice secundario na forma de tuplas
    '''
    reg = read_registry(file)
    while reg:
        lst.append((reg[0], int(reg[1])))
        reg = read_registry(file)

#Funções básicas de leitura e escrita ----------------------------------------|

def read_registry(file) -> list:
    '''
    lê o próximo registro do arquivo *file* e retorna ele em forma de lista de strings
    '''
    b_size = file.read(2)
    if b_size == b"":
        return []
    size = int.from_bytes(b_size, "little")
    registry = file.read(size).decode().split('|')
    registry.pop()
    return registry

def write_regstry(file, fields: list|tuple) -> None:
    '''
    escreve um registro de tamanho variavel separado por '|', contendo seu tamanho
    em 2 bytes no formato little ending no inicio, de campos contidos em *fields*
    '''
    reg = ''
    for field in fields:
        reg = reg + str(field) + '|'
    byte_reg = reg.encode()
    size = int.to_bytes(len(reg), 2, "little")
    file.write(size)
    file.write(byte_reg)

main()