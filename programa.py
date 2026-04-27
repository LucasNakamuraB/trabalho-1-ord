import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--build', action="store_true", help="Gera novo arquivo de indices")
parser.add_argument('-e', '--execute', metavar='filename', help="Executa o arquivo de comandos")
parser.add_argument('-c', '--compact', action="store_true", help="Compacta o arquivo \"games.dat\"")

args = parser.parse_args()

in_file = open("games.dat", 'rb+')

fields = ["id", "nome", "ano", "genero", "publicadora", "plataforma"]

def main() -> None:
    if args.build:
        print('-- Construindo índice --')
        print('-- Índice construído --')
        a = read_registry(in_file)
        while a != []:
            print(a)
            a = read_registry(in_file)
    elif args.execute:
        print("-- arquivo de instruções: "+ str(args.execute) + " aberto --")
    if args.compact:
        print("-- Compactando arquivo --")
        print("-- Arquivo compactado --")
    

def generate_indexes() -> None:
    '''
    Gera arquívos de índices ou sobrescreve os atuais
    '''
    pass

def generate_primary_index():
    '''
    Gera um arquivo de indices primários ou substitui caso já houver
    '''

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
    Insere um índice (uma string no formato "*id|byte-offset*") de forma ordenada
    conforme o *id* em *lst*
    '''
    pass


main()