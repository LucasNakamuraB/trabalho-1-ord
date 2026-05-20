import os
import argparse
import bisect
from struct import pack, unpack, calcsize

primary_format = "ii"
reverse_format = "iii"

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--build', action="store_true", help="Gera novo arquivo de indices")
parser.add_argument('-e', '--execute', metavar='filename', help="Executa o arquivo de comandos")
parser.add_argument('-c', '--compact', action="store_true", help="Compacta o arquivo \"games.dat\"")

args = parser.parse_args()

# Abre o arquivo games.dat. Se não existir, cria um vazio para evitar erro no open rb+
if not os.path.exists("games.dat"):
    open("games.dat", 'wb').close()
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
        print('what')
        print('-- Construindo índice --')
        generate_indexes()
        print('-- Índice construído --')
        
    elif args.execute:
        print("-- Arquivo de instruções: "+ str(args.execute) + " aberto --")
        load_indexes()
        execute(args.execute)
        
        # Salva os índices após a execução das operações
        generate_inversa_file()
        generate_file("genero.ind", genero_index)
        generate_file("publicadora.ind", publicadora_index)
        p_file = open("primario.ind", "wb")
        for idx in primary_index:
            p_file.write(pack(primary_format, idx[0], idx[1]))
        p_file.close()

        # print(primary_index)
        #print(lista_inversa)
        # print(genero_index)
        #print(publicadora_index)
        print("-- Instruções concluídas --")
    elif args.compact:
        in_file.close()
        compact()

#Execução de operações -------------------------------------------------------|

def execute(filename: str) -> None:
    '''
    Recebe o nome de um arquivo de texto e realiza as operações contidas nele
    '''
    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as f_ops:
            for linha in f_ops:
                linha = linha.strip()
                if not linha: continue
                interpretate(linha)
    else:
        print(f"Erro: Arquivo '{filename}' não encontrado.")

def interpretate(operat: str):
    '''
    interpreta a operação descrita em *operat* e realiza a função de acordo
    '''
    partes = operat.split(' ', 1)
    op = partes[0]
    argumento = partes[1] if len(partes) > 1 else ""
    
    if op == "bp":
        id_search(int(argumento))
    elif op == "bs1":
        genero_search(argumento)
    elif op == "bs2":
        publicadora_search(argumento)
    elif op == "i":
        insert(argumento)
    elif op == "r":
        remove(int(argumento))

def id_search(id: int) -> list:
    '''
    recebe um *id* de jogo e procura ele no indice primario, existir, retorna
    o registro lido por *read_registry()*, se não, retorna uma lista vazia
    '''
    print(f"Busca pelo registro de ID \"{id}\"")
    idx = bisect.bisect_left(primary_index, (id, 0))
    if idx < len(primary_index) and primary_index[idx][0] == id:
        offset = primary_index[idx][1]
        in_file.seek(offset)
        reg = read_registry(in_file)
        if reg and not reg[0].startswith('*'):
            print('|'.join(reg) + '|')
            return reg
    print("Registro não encontrado!")
    return []

def genero_search(gen: str) -> list:
    '''
    procura na lista secundária de generos os jogos de genero *gen*,
    e retorna uma lista deles, ou lista vazia se o genero for inválido
    '''
    head = -1
    for g, h in genero_index:
        if g == gen:
            head = h
            break
    
    encontrados = []
    if head != -1:
        atual = head
        while atual != -1:
            item = lista_inversa[atual]
            gid = item[0]
            if gid != -1:
                # busca offset no indice primario
                idx = bisect.bisect_left(primary_index, (gid, 0))
                if idx < len(primary_index) and primary_index[idx][0] == gid:
                    encontrados.append((gid, primary_index[idx][1]))
            atual = item[1] # prox_gen
            
    encontrados.sort()
    print(f"Busca por registros de gênero \"{gen}\" ({len(encontrados)} registros)")
    for gid, off in encontrados:
        in_file.seek(off)
        reg = read_registry(in_file)
        print('|'.join(reg) + '|')
    return encontrados

def publicadora_search(pub: str) -> list:
    '''
    procura na lista secundária de publicadoras os jogos de publicadora *pub*,
    e retorna uma lista deles, ou lista vazia se a poblucadora for inválida
    '''
    head = -1
    for p, h in publicadora_index:
        if p == pub:
            head = h
            break
            
    encontrados = []
    if head != -1:
        atual = head
        while atual != -1:
            item = lista_inversa[atual]
            gid = item[0]
            if gid != -1:
                idx = bisect.bisect_left(primary_index, (gid, 0))
                if idx < len(primary_index) and primary_index[idx][0] == gid:
                    encontrados.append((gid, primary_index[idx][1]))
            atual = item[2] # prox_pub
            
    encontrados.sort()
    print(f"Busca por registros de publicadora \"{pub}\" ({len(encontrados)} registros)")
    for gid, off in encontrados:
        in_file.seek(off)
        reg = read_registry(in_file)
        print('|'.join(reg) + '|')
    return encontrados

def insert(registry: str):
    '''
    Insere o registro em *games.dat*, se o id não for repetido
    '''
    partes = registry.split('|')
    try:
        gid = int(partes[0])
    except:
        return

    print(f"Inserção do registro de chave \"{gid}\"", end="")
    
    idx = bisect.bisect_left(primary_index, (gid, 0))
    if idx < len(primary_index) and primary_index[idx][0] == gid:
        print(f"\nErro: ID {gid} duplicado!")
        return

    if not registry.endswith('|'):
        registry += '|'
    
    byte_reg = registry.encode('utf-8')
    tam = len(byte_reg)
    print(f" ({tam} bytes)")
    
    in_file.seek(0, os.SEEK_END)
    offset = in_file.tell()
    in_file.write(int.to_bytes(tam, 2, "little"))
    in_file.write(byte_reg)
    in_file.flush()
    
    primary_index.append((gid, offset))
    primary_index.sort()
    
    gen = partes[3]
    pub = partes[4]
    
    # Atualiza gênero
    pos_gen = check_sec_for(genero_index, gen)
    if pos_gen == -1:
        i = add_inversa_single(gid)
        genero_index.append((gen, i))
        genero_index.sort()
    else:
        add_to_inversa(pos_gen, 3, gid)
        
    # Atualiza publicadora
    pos_pub = check_sec_for(publicadora_index, pub)
    if pos_pub == -1:
        i = add_inversa_single(gid)
        publicadora_index.append((pub, i))
        publicadora_index.sort()
    else:
        add_to_inversa(pos_pub, 4, gid)

def remove(id: int):
    '''
    remove lógicamente o registro de *id* do arquivo, e atualiza os índices 
    '''
    print(f"Remoção do registro de chave \"{id}\"", end="")
    idx = bisect.bisect_left(primary_index, (id, 0))
    if idx >= len(primary_index) or primary_index[idx][0] != id:
        print("\nRegistro não encontrado!")
        return
            
    offset = primary_index[idx][1]
    print(f" (offset = {offset})")
    
    in_file.seek(offset + 2)
    in_file.write(b'*')
    in_file.flush()
            
    primary_index.pop(idx)
    
    global lista_inversa
    for i in range(len(lista_inversa)):
        if lista_inversa[i][0] == id:
            item = lista_inversa[i]
            lista_inversa[i] = (-1, item[1], item[2])
            break

def compact() -> None:
    '''
    Compacta o arquivo games.dat removendo registros marcados com *
    '''
    print("-- Compactando arquivo --")
    file = open("games.dat", "rb+")
    temp_name = "temp_games.dat"
    f_novo = open(temp_name, "wb")
    file.seek(0)
    while True:
        reg = read_registry(file)
        if reg == []: break
        if reg[0].startswith('*'): continue
        write_regstry(f_novo, reg)
    f_novo.close()
    
    file.close()
    os.remove("games.dat")
    os.rename(temp_name, "games.dat")
    in_file = open("games.dat", "rb+")
    generate_indexes()
    print("-- Arquivo compactado --")

#Geração de índices ----------------------------------------------------------| 

def generate_indexes() -> None:
    '''
    Gera os arquívos de índices ou sobrescreve os atuais
    '''
    global in_file
    in_file = open("games.dat", "rb+")
    global primary_index, genero_index, publicadora_index, lista_inversa
    primary_index = []
    lista_inversa = []
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
    in_file.seek(0)
    reg = ['buxa']
    while reg != []:
        offset = in_file.tell()
        reg = read_registry(in_file)
        if reg and not reg[0].startswith('*'):
            primary_index.append((int(reg[0]), offset))
    primary_index.sort()
    for idx in primary_index:
        primario.write(pack(primary_format, idx[0], idx[1]))
    primario.close()

def generate_secondary_index(field_index: int) -> list[tuple]:
    '''
    Gera um índice secundário do campo de indice *field_index* em *fields*, e
    adiciona ele à lista inversa
    '''
    secondary = []
    for index in primary_index:
        in_file.seek(index[1])
        reg = read_registry(in_file)
        pos = check_sec_for(secondary, reg[field_index])
        if len(secondary) == 0 or pos == -1:
            i = add_inversa_single(int(reg[0]))
            secondary.append((reg[field_index], i))
        else:
            add_to_inversa(pos, field_index, int(reg[0]))
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
    while i < len(lst) and not found:
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
    next_idx = field - 2
    item = lista_inversa[pos]
    if item[next_idx] == -1:
        a = add_inversa_single(id)
        new_tup = list(item)
        new_tup[next_idx] = a
        lista_inversa[pos] = tuple(new_tup)
    else:
        add_to_inversa(item[next_idx], field, id)

def add_inversa_single(id: int) -> int:
    '''
    Usado caso um item seja the first de seu indice secundario,
    procura um item de mesmo *id*, o atualiza e retorna sua posição, se nao,
    adiciona ao fim da lista
    '''
    i = 0
    found = False
    while not found and i < len(lista_inversa):
        item = lista_inversa[i]
        if item[0] == id:
            found = True
        else:
            i += 1
            
    if not found:
        lista_inversa.append((id, -1, -1))
        return len(lista_inversa) - 1
    else:
        return i

#Geração de arquivos ---------------------------------------------------------|

def generate_file(name: str, lst: list):
    '''
    Escreve os campos de *lst* para um arquivo de nome *name* usando a função
    *write_regstry()* e retorna ele
    '''   
    file = open(name, 'wb')
    for index in lst:
        write_regstry(file, index)
    return file

def generate_inversa_file():
    '''
    gera um arquivo binario com base na *lista_inversa*
    '''
    inversa_file = open("listaInvertida.lst", "wb")
    for i in lista_inversa:
        idx_bytes = pack(reverse_format, i[0], i[1], i[2])
        inversa_file.write(idx_bytes)
    inversa_file.close()

#Carregamento de índices -----------------------------------------------------|

def load_indexes() -> None:
    '''
    carrega os arquivos de indice em suas respectivas listas
    '''
    global primary_index, lista_inversa, genero_index, publicadora_index
    primary_index = load_primary_index()
    lista_inversa = load_inversa()
    
    genero_index = []
    if os.path.exists("genero.ind"):
        g_file = open("genero.ind", 'rb')
        load_secundaria(g_file, genero_index)
        g_file.close()
        
    publicadora_index = []
    if os.path.exists("publicadora.ind"):
        p_file = open("publicadora.ind", 'rb')
        load_secundaria(p_file, publicadora_index)
        p_file.close()

def load_primary_index() -> list:
    '''
    carrega o arquivo *primario.ind* em uma *primary_index* em formato 
    *(indice, byte-offset)* 
    '''
    lst = []
    if os.path.exists("primario.ind"):
        primario =  open("primario.ind", "rb")
        idx_bytes = primario.read(calcsize(primary_format))
        while idx_bytes:
            idx = unpack(primary_format, idx_bytes)
            lst.append(idx)
            idx_bytes = primario.read(calcsize(primary_format))
        primario.close()
    return lst

def load_inversa() -> list:
    '''
    Retorna uma lista contendo os indices da lista inversa na forma de tuplas
    '''
    lst = []
    # Usando o nome que está no workspace
    filename = "listaInvertida.lst"
    if os.path.exists(filename):
        inv_file =  open(filename, "rb")
        idx_bytes = inv_file.read(calcsize(reverse_format))
        while idx_bytes:
            idx = unpack(reverse_format, idx_bytes)
            lst.append(idx)
            idx_bytes = inv_file.read(calcsize(reverse_format))
        inv_file.close()
    return lst
      
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
    registry_bytes = file.read(size)
    registry = registry_bytes.decode('utf-8').split('|')
    if registry[-1] == "":
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
    byte_reg = reg.encode('utf-8')
    size = int.to_bytes(len(byte_reg), 2, "little")
    file.write(size)
    file.write(byte_reg)

if __name__ == "__main__":
    main()
