import os
import argparse
from struct import pack, unpack, calcsize

primary_format = "ii"

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--build', action="store_true", help="Gera novo arquivo de indices")
parser.add_argument('-e', '--execute', metavar='filename', help="Executa o arquivo de comandos")
parser.add_argument('-c', '--compact', action="store_true", help="Compacta o arquivo \"games.dat\"")

args = parser.parse_args()

in_file = open("games.dat", 'rb+')
primario = None
genero = None
publicadora = None


fields = ["id", "nome", "ano", "genero", "publicadora", "plataforma"]

primary_index: list = []

def main() -> None:
    if not args.build:
        #genero = open("genero.ind", "rb")
        #publicadora = open("publicadora.ind", "rb")
        pass

    if args.build:
        print('-- Construindo índice --')
        generate_indexes()
        print('-- Índice construído --')
        
    elif args.execute:
        print("-- Arquivo de instruções: "+ str(args.execute) + " aberto --")
        primary_index = load_primary_index()
        print("-- Instruções concluídas --")
    elif args.compact:
        print("-- Compactando arquivo --")
        print("-- Arquivo compactado --")
    

def generate_indexes() -> None:
    '''
    Gera os arquívos de índices ou sobrescreve os atuais
    '''
    generate_primary_index()


def generate_primary_index():
    '''
    Gera um arquivo de indices primários ou substitui caso já houver
    '''
    primario = open("primario.ind", "wb+")
    reg = ['buxa']
    while reg != []:
        offset = in_file.seek(0, os.SEEK_CUR)
        reg = read_registry(in_file)
        if reg:
            ordered_index_insert(primary_index, int(reg[0]), offset)
    for idx in primary_index:
        primario.write(pack(primary_format, idx[0], idx[1]))

def load_primary_index() -> list[tuple]:
    '''
    carrega o arquivo *primario.ind* em uma lista de tuplas em formato 
    *(indice, byte-offset)* e retorna ela
    '''
    primary_list = []
    primario =  open("primario.ind", "rb")
    idx_bytes = primario.read(calcsize(primary_format))
    while idx_bytes:
        idx = unpack(primary_format, idx_bytes)
        primary_list.append(idx)
        idx_bytes = primario.read(calcsize(primary_format))
    return primary_list


def generate_secondary_index(field_index: int):
    '''
    Gera um índice secundário do campo de indice *field_index* em *fields*
    '''
    index_name = fields[field_index] + ".ind"

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

def ordered_index_insert(lst: list, id: int, offset: int) -> None:
    '''
    Insere um índice na forma de tupla (*id*, *offset*) de forma ordenada
    conforme o *id* em *lst*
    '''
    #PROVISORIO
    lst.append((id, offset))


main()