import random
import serial
import secrets
import hashlib
import time
from scipy.stats import chisquare
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

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



# CODIFICANDO


def bits_to_bytes(bits):
    return np.packbits(bits[:256]).tobytes() # pega apenas os primeiros 256 bits, agrupa de 8 em 8 (packbits) e converte para bytes

def derivar_material(bits):
    raw = bits_to_bytes(bits)
    digest = hashlib.sha256(raw).digest() # aplica SHA-256 (transforma um dado em uma sequência fixa de bits)
    key = digest[:32] # usa 32 bytes como chave AES-256
    iv = digest[:16] # usa 32 bytes como chave AES-256
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


def ataque_random_seed(ciphertext, mensagem, max_seed=20000):
    print("\n[ATAQUE] Tentando descobrir seed do random()...")
    inicio = time.time() # marca início do ataque

    for seed in range(max_seed): # testa seeds possíveis
        random.seed(seed)
        tentativa = gen_random_bits(256) # tenta descriptografar

        texto = decrypt(tentativa, ciphertext)

        if texto == mensagem:  # se acertar
            tempo = time.time() - inicio
            print("Seed encontrada:", seed)
            print("Tempo para quebrar:", round(tempo,4), "segundos")
            return tempo, True, tentativa, texto

    tempo = time.time() - inicio
    print("Seed não encontrada após", max_seed, "tentativas.")
    print("Tempo gasto:", round(tempo,4), "segundos")
    return tempo, False, None, None


def ataque_forca_bruta_limitada(ciphertext, mensagem, tentativas=100000):
    # gera chaves aleatórias usando secrets e tenta descriptografar

    print("\n[ATAQUE] Iniciando força bruta limitada...")
    inicio = time.time()

    for i in range(tentativas): 
        tentativa = gen_secrets_bits(256) # tenta várias chaves aleatórias

        texto = decrypt(tentativa, ciphertext)  # gera chave candidata

        if texto == mensagem:
            tempo = time.time() - inicio
            print("Chave encontrada após", i, "tentativas")
            print("Tempo:", round(tempo,4), "segundos")
            return tempo, True, tentativa, texto

    tempo = time.time() - inicio
    print("Ataque falhou após", tentativas, "tentativas.")
    print("Tempo gasto:", round(tempo,4), "segundos")
    return tempo, False, None, None


# EXECUÇÃO

if __name__ == "__main__":

    mensagem = input("Mensagem:")
    print("\n================ INÍCIO DO EXPERIMENTO ================\n")
    print("Mensagem original:", mensagem)

    print("\n================ ANÁLISE ESTATÍSTICA ================\n")

    # 1) random()
    print("\n--- Grupo: random() ---")
    random.seed(1234)
    bits_random = gen_random_bits(256)
    analisar("random()", bits_random)
    cipher_random = encrypt(bits_random, mensagem)

    # 2) secrets()
    print("\n--- Grupo: secrets() ---")
    bits_secrets = gen_secrets_bits(256)
    analisar("secrets()", bits_secrets)
    cipher_secrets = encrypt(bits_secrets, mensagem)

    # 3) Físico Cru
    print("\n--- Grupo: Físico Cru ---")
    bits_fisico = gen_fisico_fraco(256)
    analisar("Físico Cru", bits_fisico)
    cipher_fisico = encrypt(bits_fisico, mensagem)
 
    # 4) Físico + Hash
    print("\n--- Grupo: Físico + SHA256 ---")
    bits_fisico_hash = hash_extracao(bits_fisico)
    analisar("Físico + Hash", bits_fisico_hash)
    cipher_fisico_hash = encrypt(bits_fisico_hash, mensagem)


    # ATAQUES
    print("\n================ INICIANDO ATAQUES ================\n")

    tempo_random, sucesso_random, chave_random, msg_random = ataque_random_seed(cipher_random, mensagem)

    tempo_fisico, sucesso_fisico, chave_fisico, msg_fisico = ataque_forca_bruta_limitada(cipher_fisico, mensagem)

    tempo_fisico_hash, sucesso_fisico_hash, chave_fisico_hash, msg_fisico_hash = ataque_forca_bruta_limitada(cipher_fisico_hash, mensagem)

    tempo_secrets, sucesso_secrets, chave_secrets, msg_secrets = ataque_forca_bruta_limitada(cipher_secrets, mensagem)

    
    # RELATÓRIO FINAL
    print("\n================ RELATÓRIO FINAL ================")

    def mostrar(nome, sucesso, tempo, mensagem_recuperada):
        print(f"\n{nome}:")
        print("   Quebrado?", sucesso)
        print("   Tempo:", round(tempo,4), "s")
        if sucesso:
            print("   Mensagem recuperada pelo ataque:", mensagem_recuperada)
        else:
            print("   Mensagem recuperada pelo ataque: NÃO FOI POSSÍVEL DECIFRAR")

    mostrar("random()", sucesso_random, tempo_random, msg_random)
    mostrar("Físico Cru", sucesso_fisico, tempo_fisico, msg_fisico)
    mostrar("Físico + Hash", sucesso_fisico_hash, tempo_fisico_hash, msg_fisico_hash)
    mostrar("secrets()", sucesso_secrets, tempo_secrets, msg_secrets)

    print("\n================ FIM DO EXPERIMENTO ================")