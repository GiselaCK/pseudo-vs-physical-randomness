import random
import serial
import secrets
import hashlib
import time
from scipy.stats import chisquare
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from tqdm import tqdm
import matplotlib.pyplot as plt

#ANÁLISE ESTATÍSTICA

def entropia(bits):
    # Fórmula: H = -p log2(p) - (1-p) log2(1-p) (p = frequência de "1")
    # Próximo de 0 = sequência previsível
    # Máximo = 1 bit (quando p= 0.5)

    p = sum(bits)/len(bits) # calcula a frequência de "1"
    if p == 0 or p == 1:
        return 0
    return -p*np.log2(p) - (1-p)*np.log2(1-p) #fórmula da entropia

def autocorrelacao(bits):
    # Mede a correlação entre bits consecutivos (lag 1), comparando bits[:-1] e bits[1:] e usando a correlação de Pearson.
    # Ideal em aleatoriedade: 0

    bits = np.array(bits)
    if len(bits) < 2:
        return 0
    return np.corrcoef(bits[:-1], bits[1:])[0,1] #função de correlação

def p_valor_uniformidade(bits):
    #verifica se a distribuição observada é compatível com uma distribuição uniforme
    bits = np.array(bits)

    # Conta quantos 0s e 1s existem
    freq_observada = np.bincount(bits, minlength=2)

    # Esperado para distribuição uniforme binária (50% 0, 50% 1)
    esperado = [len(bits)/2, len(bits)/2]

    # Teste qui-quadrado comparando observado vs esperado
    _, p_valor = chisquare(freq_observada, f_exp=esperado)

    return p_valor


#imprimindo análise
def analisar(nome, bits):
    print(f"\n ANÁLISE: {nome}")
    print("Total de bits:", len(bits))
    print("Frequência de 1s:", round(sum(bits)/len(bits), 4))
    print("Entropia de Shannon:", round(entropia(bits), 4))
    print("Autocorrelação:", round(autocorrelacao(bits), 4))
    print("P-valor de uniformidade:", round(p_valor_uniformidade(bits), 4))
    freq_1 = sum(bits)/len(bits)
    autocorr = autocorrelacao(bits)
    return freq_1, autocorr

def gen_markov_bits(n, freq_1, autocorr):
    """
    Gera sequência binária com:
    - frequência aproximada freq_1
    - dependência lag-1 aproximada autocorr
    """

    # converte autocorrelação em probabilidade de permanência
    p_stay = (1 + autocorr) / 2

    # garante limites válidos
    p_stay = max(0.0, min(1.0, p_stay))

    # escolhe bit inicial baseado na frequência observada
    first = 1 if random.random() < freq_1 else 0
    bits = [first]

    for _ in range(n - 1):
        if random.random() < p_stay:
            bits.append(bits[-1])
        else:
            bits.append(1 - bits[-1])

    return bits

# CODIFICANDO


def bits_to_bytes(bits):
    return np.packbits(bits[:256]).tobytes() # pega apenas os primeiros 256 bits, agrupa de 8 em 8 (packbits) e converte para bytes

def derivar_material(bits):
    raw = bits_to_bytes(bits)
    key = raw[:32] # usa 32 bytes como chave AES-256
    iv = raw[:16] # usa 16 bytes como vetor de inicialização
    return key, iv

def encrypt(bits, mensagem):
    key, iv = derivar_material(bits)
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend()) # cria cifra AES em modo CTR
    encryptor = cipher.encryptor() # objeto de criptografia
    return encryptor.update(mensagem.encode())  # retorna ciphertext

def decrypt(bits, ciphertext):
    key, iv = derivar_material(bits)
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext).decode(errors="ignore")


# GERADORES 

def gen_random_bits(n):
    # grupo random (Mersenne Twister)
    return [random.getrandbits(1) for _ in range(n)]

def gen_secrets_bits(n):
    # grupo secrets
    return [secrets.randbits(1) for _ in range(n)]

def gen_fisico_fraco(n):
    # Coleta 256 bits reais do Arduino via serial.

    bits = []

    # abre porta serial
    ser = serial.Serial('COM3', 115200, timeout=1)

    print("Aguardando bits do Arduino...")

    while len(bits) < n:
        linha = ser.readline().decode().strip()

        if linha in ("0", "1"):
            bits.append(int(linha))

    ser.close()
    print("\nColeta concluída.")

    return bits

def hash_extracao(bits):
    # Aplica SHA-256 para "extrair entropia" e remover viés estatístico.

    raw = bits_to_bytes(bits)
    digest = hashlib.sha256(raw).digest()
    return list(np.unpackbits(np.frombuffer(digest, dtype=np.uint8)))


# ATAQUES


def ataque(ciphertext, mensagem, freq_1, autocorr,
           max_seed=20000, tentativas=100000):

    # ---------------- Seed attack ----------------
    print("Iniciando ataque por seed...")
    inicio = time.time()

    for seed in range(max_seed):
        random.seed(seed)
        tentativa = gen_random_bits(256)

        if decrypt(tentativa, ciphertext) == mensagem:
            tempo = time.time() - inicio
            print("Seed encontrada:", seed)
            print("Tempo:", round(tempo, 4), "s")
            return tempo, True, tentativa, mensagem

    print("Seed não encontrada.")
    print("Iniciando ataque estatístico...")

    # ---------------- Ataque estatístico ----------------
    inicio = time.time()

    for i in range(tentativas):

        tentativa = gen_markov_bits(256, freq_1, autocorr)

        if decrypt(tentativa, ciphertext) == mensagem:
            tempo = time.time() - inicio
            print("Chave encontrada via restrição estatística.")
            print("Tempo:", round(tempo,4), "s")
            return tempo, True, tentativa, mensagem

    print("Ataque estatístico falhou.")
    print("Iniciando força bruta limitada...")

    # ---------------- Força bruta controle ----------------
    inicio = time.time()

    for i in range(tentativas):
        tentativa = gen_secrets_bits(256)
        if decrypt(tentativa, ciphertext) == mensagem:
            tempo = time.time() - inicio
            print("Chave encontrada via força bruta.")
            print("Tempo:", round(tempo,4), "s")
            return tempo, True, tentativa, mensagem

    tempo = time.time() - inicio
    print("Ataque falhou.")
    return tempo, False, None, None



# EXECUÇÃO
if __name__ == "__main__":

    print("\n================ INÍCIO DO EXPERIMENTO ESTATÍSTICO ================\n")
    print("Realizando 10000 iterações de análise para cada fonte...\n")
    
    NUM_ITERACOES = 10000
    NUM_BITS = 256

    # COLETA UMA POOL GRANDE DE BITS FÍSICOS UMA ÚNICA VEZ
    print("\nColetando pool de bits físicos do Arduino...\n")
    pool_fisica = gen_fisico_fraco(NUM_ITERACOES * NUM_BITS + 1000)
    

    def sample_pool(pool, n):
        start = random.randint(0, len(pool) - n)
        return pool[start:start+n]

    resultados = {
        'random': {'freq_1': [], 'entropia': [], 'p_valor': [], 'autocorr': []},
        'secrets': {'freq_1': [], 'entropia': [], 'p_valor': [], 'autocorr': []},
        'fisico_cru': {'freq_1': [], 'entropia': [], 'p_valor': [], 'autocorr': []},
        'fisico_hash': {'freq_1': [], 'entropia': [], 'p_valor': [], 'autocorr': []}
    }

    for _ in tqdm(range(NUM_ITERACOES), desc="Progresso"):

        # RANDOM
        bits_random = gen_random_bits(NUM_BITS)
        resultados['random']['freq_1'].append(sum(bits_random)/NUM_BITS)
        resultados['random']['entropia'].append(entropia(bits_random))
        resultados['random']['p_valor'].append(p_valor_uniformidade(bits_random))
        resultados['random']['autocorr'].append(autocorrelacao(bits_random))

        # SECRETS
        bits_secrets = gen_secrets_bits(NUM_BITS)
        resultados['secrets']['freq_1'].append(sum(bits_secrets)/NUM_BITS)
        resultados['secrets']['entropia'].append(entropia(bits_secrets))
        resultados['secrets']['p_valor'].append(p_valor_uniformidade(bits_secrets))
        resultados['secrets']['autocorr'].append(autocorrelacao(bits_secrets))

        # FÍSICO CRU
        bits_fisico = sample_pool(pool_fisica, NUM_BITS)
        resultados['fisico_cru']['freq_1'].append(sum(bits_fisico)/NUM_BITS)
        resultados['fisico_cru']['entropia'].append(entropia(bits_fisico))
        resultados['fisico_cru']['p_valor'].append(p_valor_uniformidade(bits_fisico))
        resultados['fisico_cru']['autocorr'].append(autocorrelacao(bits_fisico))

        # FÍSICO + HASH
        bits_fisico_hash = hash_extracao(bits_fisico)
        resultados['fisico_hash']['freq_1'].append(sum(bits_fisico_hash)/len(bits_fisico_hash))
        resultados['fisico_hash']['entropia'].append(entropia(bits_fisico_hash))
        resultados['fisico_hash']['p_valor'].append(p_valor_uniformidade(bits_fisico_hash))
        resultados['fisico_hash']['autocorr'].append(autocorrelacao(bits_fisico_hash))


    print("\n\n================ GERANDO GRÁFICOS ================\n")

    cores = {'random': 'yellow', 'secrets': 'green', 'fisico_cru': 'red', 'fisico_hash': 'blue'}
    labels = {'random': 'random()', 'secrets': 'secrets()', 
              'fisico_cru': 'Físico Cru', 'fisico_hash': 'Físico + Hash'}

    # FREQUÊNCIA
    plt.figure(figsize=(12,6))
    for fonte in ['fisico_hash','fisico_cru','random','secrets']:
        plt.plot(resultados[fonte]['freq_1'],
                 color=cores[fonte],
                 alpha=0.7,
                 linewidth=0.5,
                 label=labels[fonte])

    plt.axhline(y=0.5,color='black',linestyle='--')
    plt.title("Frequência de 1s (10000 execuções)")
    plt.xlabel("Iteração")
    plt.ylabel("Frequência")
    plt.legend()
    plt.grid(True)
    plt.show()


    # ENTROPIA
    plt.figure(figsize=(12,6))
    for fonte in ['fisico_hash','fisico_cru','random','secrets']:
        plt.plot(resultados[fonte]['entropia'],
                 color=cores[fonte],
                 alpha=0.7,
                 linewidth=0.5,
                 label=labels[fonte])

    plt.axhline(y=1,color='black',linestyle='--')
    plt.title("Entropia de Shannon")
    plt.xlabel("Iteração")
    plt.ylabel("Entropia")
    plt.legend()
    plt.grid(True)
    plt.show()


    # AUTOCORRELAÇÃO
    plt.figure(figsize=(12,6))
    for fonte in ['fisico_hash','fisico_cru','random','secrets']:
        plt.plot(resultados[fonte]['autocorr'],
                 color=cores[fonte],
                 alpha=0.7,
                 linewidth=0.5,
                 label=labels[fonte])

    plt.axhline(y=0,color='black',linestyle='--')
    plt.title("Autocorrelação (lag 1)")
    plt.xlabel("Iteração")
    plt.ylabel("Autocorrelação")
    plt.legend()
    plt.grid(True)
    plt.show()


    print("\n================ RESUMO ESTATÍSTICO ================\n")

    for fonte in ['random','secrets','fisico_cru','fisico_hash']:
        print(f"\n--- {labels[fonte]} ---")
        print("freq média:", round(np.mean(resultados[fonte]['freq_1']),4))
        print("entropia média:", round(np.mean(resultados[fonte]['entropia']),4))
        print("autocorr média:", round(np.mean(resultados[fonte]['autocorr']),4))
        print("pvalor médio:", round(np.mean(resultados[fonte]['p_valor']),4))


    print("\n================ INÍCIO DOS ATAQUES ================\n")

    mensagem = input("Mensagem:")

    random.seed(1234)
    bits_random = gen_random_bits(256)
    cipher_random = encrypt(bits_random, mensagem)

    bits_secrets = gen_secrets_bits(256)
    cipher_secrets = encrypt(bits_secrets, mensagem)

    bits_fisico = sample_pool(pool_fisica,256)
    cipher_fisico = encrypt(bits_fisico, mensagem)

    bits_fisico_hash = hash_extracao(bits_fisico)
    cipher_fisico_hash = encrypt(bits_fisico_hash, mensagem)

    tempo_random, sucesso_random, chave_random, msg_random = ataque(cipher_random, mensagem, np.mean(resultados['random']['freq_1']), np.mean(resultados['random']['autocorr']))

    tempo_fisico, sucesso_fisico, chave_fisico, msg_fisico = ataque(cipher_fisico, mensagem, np.mean(resultados['fisico_cru']['freq_1']), np.mean(resultados['fisico_cru']['autocorr']))

    tempo_fisico_hash, sucesso_fisico_hash, chave_fisico_hash, msg_fisico_hash = ataque(cipher_fisico_hash, mensagem, np.mean(resultados['fisico_hash']['freq_1']), np.mean(resultados['fisico_hash']['autocorr']))

    tempo_secrets, sucesso_secrets, chave_secrets, msg_secrets = ataque(cipher_secrets, mensagem, np.mean(resultados['secrets']['freq_1']), np.mean(resultados['secrets']['autocorr']))
