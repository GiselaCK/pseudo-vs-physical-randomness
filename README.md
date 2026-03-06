# Aleatoriedade vs Pseudoaleatoriedade  
## Demonstrando a importância do gerador de chaves em Criptografia Simétrica através de uma simulação simplificada em Python

---

**Evento:** IV Encontro do PGMAT  
**Data:** 12 e 13 de março de 2026  
**Modalidade:** Apresentação de pôster  

**Aluna:** Gisela Ceresér Kassick  
**Orientador:** Dr. Daniel Roberto Cassar  

**Instituição:** Ilum – Escola de Ciência  
Centro Nacional de Pesquisa em Energia e Materiais (CNPEM)  

Campinas – Brasil  
Março, 2026

---

**Aleatoriedade vs Pseudoaleatoriedade: demonstrando a importância do gerador de chaves em Criptografia Simétrica através de uma simulação simplificada em Python** é um projeto experimental que investiga o impacto da qualidade da aleatoriedade na segurança de sistemas criptográficos.

O trabalho compara diferentes fontes de geração de números aleatórios — pseudoaleatórias, criptograficamente seguras e físicas — analisando suas propriedades estatísticas e seu comportamento prático na geração de chaves utilizadas em criptografia simétrica com AES-256.

---

# Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Metodologia](#metodologia)
- [Como Executar](#como-executar)
- [Especificações Técnicas](#especificações-técnicas)
- [Resultados](#resultados)
- [Referências](#referências)
- [Orientador](#orientador)
- [Autora](#autora)

---

# Sobre o projeto

A geração de números aleatórios é fundamental para a segurança da criptografia moderna. Chaves criptográficas, vetores de inicialização e nonces dependem da existência de sequências imprevisíveis.

Nem todos os geradores de números aleatórios possuem as mesmas propriedades. Enquanto **PRNGs** produzem sequências determinísticas a partir de uma seed, **CSPRNGs** utilizam fontes seguras do sistema operacional, e **TRNGs** exploram fenômenos físicos imprevisíveis, como ruído térmico.

Este projeto investiga como diferentes fontes de aleatoriedade influenciam:

- a **qualidade estatística das sequências geradas**
- a **segurança prática de chaves criptográficas**

A pergunta central do trabalho é:

> Diferenças na origem da aleatoriedade impactam, na prática, a segurança de um sistema simples de criptografia simétrica?

---

# Metodologia

O experimento combina **análise estatística** das sequências geradas com **simulações de ataque criptográfico**.

## 1. Fontes de aleatoriedade

Foram analisadas quatro fontes distintas, cada uma gerando sequências de **256 bits**:

| Fonte | Descrição |
|------|------|
| `random` | Gerador pseudoaleatório baseado no Mersenne Twister |
| `secrets` | Gerador criptograficamente seguro baseado no sistema operacional |
| Física bruta | Bits provenientes de ruído térmico medido com Arduino |
| Física + hash | Bits físicos processados com SHA-256 |

---

## 2. Coleta da fonte física

A fonte física foi obtida utilizando:

- **Arduino Leonardo**
- **resistor de 10 MΩ**
- **amplificador operacional LM358**

O circuito mede variações de **ruído térmico (Johnson–Nyquist)**.

O Arduino:

1. realiza leituras analógicas sucessivas
2. extrai o **bit menos significativo (LSB)** do ADC
3. envia os bits pela **porta serial** para o Python

Esses bits compõem a sequência física utilizada no experimento.

---

## 3. Análise estatística

Cada sequência foi avaliada utilizando três métricas principais:

### Entropia de Shannon

$$
H(X) = -\sum P(x_i)\log_2 P(x_i)
$$

Mede o grau de incerteza da distribuição.

---

### Autocorrelação

$$
R(k) = \frac{E[(X_i-\mu)(X_{i+k}-\mu)]}{\sigma^2}
$$

Detecta dependência entre bits consecutivos.

---

### Teste Qui-quadrado

$$
\chi^2 = \sum \frac{(O_i-E_i)^2}{E_i}
$$

Avalia compatibilidade com distribuição uniforme.

---

## 4. Configuração criptográfica

As sequências geradas foram utilizadas para derivar chaves criptográficas:

- **Algoritmo:** AES-256  
- **Modo:** CTR (Counter Mode)
- **Chave:** 256 bits  
- **IV:** primeiros 128 bits da sequência

A implementação foi realizada com a biblioteca **cryptography (PyCA)**.

---

## 5. Simulação de ataques

Para avaliar a segurança prática das chaves geradas foram simuladas duas estratégias de ataque.

### Reconstrução de seed

Explora o caráter determinístico do gerador `random`, tentando reproduzir a sequência original a partir de possíveis sementes.

### Força bruta estatística

Geração de múltiplas chaves a partir de um viés estatístico.
### Força bruta limitada

Geração de múltiplas chaves candidatas para tentativa de descriptografia bem-sucedida.

O critério de sucesso foi:

- recuperação completa da mensagem original
- registro do tempo necessário para o ataque

---



## Como Executar

### Requisitos

- Python 3.8+
- Arduino IDE
- Bibliotecas Python: `pyserial`, `cryptography`, `numpy`, `scipy`, `matplotlib`, `tqdm`, `time`, `random`, `secrets`.
- Arduino Leonardo (ou similar)
- Jumpers
- Resistor de 10 MΩ
- Op Amp LM358

### Instalação

```bash
git clone https://github.com/seu-usuario/RandomICS.git
cd RandomICS
pip install pyserial cryptography numpy scipy matplotlib
```

### Executando o Código

O repositório contém dois arquivos principais: `.ino` e `.py` 

**1. Configuração do Arduino para coleta de fonte física** - `.ino`

- Faça a seguinte conexão:
  
<p align="center">
  <img src="circuito.png" width="500">
</p>

- Conecte o Arduino ao computador
- Carregue o código `.ino` usando a Arduino IDE


**2. Execução do experimento completo** - `experimento.py`

```bash
python experimento.py
```

Este script irá:
- Coletar 10.000 sequências de 256 bits de cada fonte
- Calcular métricas estatísticas (entropia, autocorrelação, qui-quadrado)
- Salvar resultados em gráficos
- Derivar chaves AES-256 e IVs
- Executar tentativa de decodificação pela sequência de ataques
- Enviar relatório final

---

## Especificações Técnicas

### Linguagens e Tecnologias

- **Python** – Análise de dados, criptografia, estatística
- **C++ (Arduino IDE)** – Coleta de ruído físico via pino flutuante
- **AES-256 CTR** – Algoritmo de criptografia simétrica

### Bibliotecas Utilizadas

- **pyserial**: Comunicação serial com Arduino
- **cryptography**: Implementação AES-256 modo CTR
- **numpy/scipy**: Cálculos estatísticos
- **matplotlib**: Visualização de resultados
- **hashlib**: SHA-256 para extração de entropia
- **secrets/random**: Geradores de números aleatórios

### Estrutura do Experimento

#### Fontes de Aleatoriedade

| Fonte | Descrição | Implementação |
|-------|-----------|---------------|
| **random** | Mersenne Twister (não criptográfico) | `random.getrandbits(256)` |
| **secrets** | CSPRNG do sistema operacional | `secrets.randbits(256)` |
| **Física bruta** | Ruído térmico do resistor | Leitura LSB do pino A0 flutuante |
| **Física + hash** | Ruído bruto com extração SHA-256 | `hashlib.sha256(bits).digest()` |

#### Métricas Estatísticas


##### Entropia de Shannon

$$
H(X) = -\sum_{i} P(x_i)\,\log_2 P(x_i)
$$

Mede a incerteza da distribuição.

Para dados binários, o valor máximo é 1 bit quando:

$$
P(0) = P(1) = 0,5
$$


##### Autocorrelação

$$
R(k) = \frac{E[(X_i - \mu)(X_{i+k} - \mu)]}{\sigma^2}
$$

Detecta dependência linear entre bits separados por uma defasagem $\( k \)$.

Onde:

- $\( \mu \)$ = média da sequência  
- $\( \sigma^2 \)$ = variância  
- $\( k \)$ = defasagem (lag)

Para uma sequência aleatória ideal:

$$
R(k) \approx 0 \quad \text{para } k \ne 0
$$


##### Teste Qui-quadrado

$$
\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}
$$

Avalia compatibilidade com distribuição uniforme.

Onde:

- $\( O_i \)$ = frequência observada  
- $\( E_i \)$ = frequência esperada  
- $\( n \)$ = tamanho da amostra  

Valores elevados de $\( \chi^2 \)$ indicam desvio significativo da uniformidade.

#### Configuração Criptográfica

- **Algoritmo:** AES-256 em modo CTR
- **Chave:** 256 bits derivados da sequência
- **IV:** 128 bits derivados da sequência
- **Mensagem teste:** Input para o usuário completar

---

## Resultados
Os experimentos foram executados em **10.000 iterações independentes** para cada fonte de aleatoriedade.

### Principais observações

#### `random()`
- boas propriedades estatísticas  
- vulnerável à **reconstrução de seed**

#### `secrets()`
- comportamento estatístico próximo do ideal  
- **nenhuma vulnerabilidade observada**

#### **Fonte física bruta**
- presença de **viés** e **autocorrelação**  
- imperfeições experimentais esperadas em sistemas físicos

#### **Fonte física + SHA-256**
- **redução significativa do viés**
- comportamento estatístico **próximo do ideal**

---

Os resultados demonstram que **propriedades estatísticas aparentemente adequadas não garantem segurança criptográfica**, reforçando a necessidade de utilizar **geradores projetados especificamente para aplicações criptográficas**.


---

## Referências

BLAZHEVSKI, D. et al. **Modes of Operation of the AES Algorithm**. 2012.

CUCU LAURENCIU, N.; COTOFANA, S. D. **Low Cost and Energy, Thermal Noise Driven, Probability Modulated Random Number Generator**. Delft University of Technology, 2018.

D'APRANO, S. **PEP 506 – Adding a Secrets Module to the Standard Library**. 2015. Disponível em: https://peps.python.org/pep-0506/. Acesso em: 26 fev. 2026.

GENNARO, R. **Randomness in Cryptography**. IEEE Security & Privacy, v. 4, n. 2, p. 64-67, 2006.

KATZ, J.; LINDELL, Y. **Introduction to Modern Cryptography**. 2007.

MENGDI, Z. et al. **Overview of Randomness Test on Cryptographic Algorithms**. Journal of Physics: Conference Series, v. 1861, n. 1, 012009, 2021.

PYTHON SOFTWARE FOUNDATION. **random — geração de números pseudoaleatórios**. Disponível em: https://docs.python.org/3/library/random.html. Acesso em: 26 fev. 2026.

PYTHON SOFTWARE FOUNDATION. **secrets — geração de números seguros**. Disponível em: https://docs.python.org/3/library/secrets.html. Acesso em: 26 fev. 2026.

PYTHON SOFTWARE FOUNDATION. **hashlib — algoritmos de hash seguros**. Disponível em: https://docs.python.org/3/library/hashlib.html. Acesso em: 26 fev. 2026.

PYCA CRYPTOGRAPHY. **Cryptography Documentation**. Disponível em: https://cryptography.io. Acesso em: 26 fev. 2026.

VIGNA, S. **It Is High Time We Let Go of the Mersenne Twister**. arXiv:1910.06437, 2019. Disponível em: https://arxiv.org/abs/1910.06437. Acesso em: 26 fev. 2026.

WALTER, Daniela; BÜLAU, André; ZIMMERMANN, André. **Review on excess noise measurements of resistors**. Sensors, v. 23, n. 3, p. 1107, 2023. DOI: https://doi.org/10.3390/s23031107

---

## Professor orientador

<table>
  <tr>
    <td align="center">
      <a href="#" title="Prof. Daniel R. Cassar">
        <img src="https://avatars.githubusercontent.com/u/9871905?v=4" width="100px;" alt="Foto do Daniel no Github"/><br>
        <a href="https://github.com/drcassar"><b>Prof. Dr. Daniel R. Cassar</b></a>
      </a>
    </td>
  </tr>
</table>

---

## Aluna desenvolvedora

<table>
  <tr>
    <td align="center">
      <a href="#" title="Aluno 1">
        <img src="https://avatars.githubusercontent.com/u/164672308?v=4" width="100px;" alt="Foto do Aluno 1"/><br>
        <a href="https://github.com/GiselaCK"><b>Gisela Ceresér Kasscik</b></a>
      </a>
    </td>
   </tr>
</table>



**Licença:** Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

**Contato:** gisela.kassick@gmail.com
