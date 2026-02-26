# Aleatoriedade vs Pseudoaleatoriedade: 
## Demonstrando a importância do gerador de chaves em Criptoprafia Simétrica através de uma simulação simplicada em Python

---

**Integrantes:** Gisela Ceresér Kassick

**Instituição:** Ilum - Escola de Ciência - CNPEM

**Professor orientador:** Daniel Roberto Cassar

---

**Aleatoriedade vs Pseudoaleatoriedade: demonstrando a importância do gerador de chaves em Criptoprafia Simétrica através de uma simulação simplicada em Python** é um projeto que investiga o papel fundamental da aleatoriedade na criptografia simétrica por meio de uma abordagem experimental e comparativa. Desenvolvido em Python com integração Arduino, o projeto analisa quatro diferentes fontes de geração de números aleatórios — desde geradores pseudoaleatórios convencionais até fontes físicas de ruído —, avaliando sua qualidade estatística e seu impacto prático na segurança de um sistema criptográfico AES-256.

---

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Como Executar](#como-executar)
- [Especificações Técnicas](#especificações-técnicas)
- [Resultados](#resultados)
- [Referências](#referências)
- [Professor orientador](#professor-orientador)
- [Aluna desenvolvedora](#aluna-desenvolvedora)

---

## Sobre o projeto

A aleatoriedade é elemento central da criptografia moderna, indispensável à geração de chaves, vetores de inicialização e demais parâmetros críticos de segurança. A proteção de sistemas criptográficos depende da produção de informações que um adversário não consiga aprender ou prever; portanto, a qualidade da fonte aleatória constitui requisito essencial para a confidencialidade e a integridade das comunicações.

O presente projeto tem como **objetivo** analisar e comparar a qualidade estatística e a adequação criptográfica de diferentes fontes de geração de números aleatórios, avaliando seu impacto na criptografia simétrica através de:

- Geração de sequências binárias a partir de quatro fontes distintas:
  - **Gerador pseudoaleatório padrão (random)** – Mersenne Twister
  - **Gerador criptograficamente seguro (secrets)** – CSPRNG do sistema
  - **Fonte física bruta** – ruído térmico captado por Arduino
  - **Fonte física com extração por hash** – SHA-256 aplicado ao ruído bruto para retirar viés estatísticos

Uma vez gerada as sequências binárias, o experimento prossegue para:
- Análise **estatística** comparativa (entropia, autocorrelação, teste qui-quadrado)
- Derivação de chaves AES-256 e vetores de inicialização
- Simulação de **ataques** (reconstrução de seed e força bruta limitada)
- Avaliação do impacto prático da qualidade da aleatoriedade na segurança criptográfica

A pergunta que orienta a pesquisa é: *Diferenças na origem da aleatoriedade produzem variações estatísticas relevantes que impactam, de forma prática, a segurança de um sistema simples de criptografia simétrica?*

---

## Como Executar

### Requisitos

- Python 3.8+
- Arduino IDE
- Bibliotecas Python: `pyserial`, `cryptography`, `numpy`, `scipy`, `matplotlib`
- Arduino Uno (ou similar)
- Jumpers

### Instalação

```bash
git clone https://github.com/seu-usuario/RandomICS.git
cd RandomICS
pip install pyserial cryptography numpy scipy matplotlib
```

### Executando o Código

O repositório contém dois arquivos principais: `.ino` e `.py` 

**1. Configuração do Arduino para coleta de fonte física** - `.ino`

- Conecte um jumper ao pino analógico A0 do Arduino, deixando a outra extremidade desconectada (estado flutuante)
- Conecte o Arduino ao computador
- Carregue o código `.ino` usando a Arduino IDE

- fotooo


**2. Execução do experimento completo** - `experimento.py`

```bash
python experimento.py
```

Este script irá:
- Coletar 10.000 sequências de 256 bits de cada fonte
- Calcular métricas estatísticas (entropia, autocorrelação, qui-quadrado)
- Derivar chaves AES-256 e IVs
- Salvar resultados em arquivos CSV e gráficos
- Executar tentativa de decodificação por força limitada, registrando tempo e taxa de sucesso
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
| **Física bruta** | Ruído térmico do pino analógico | Leitura LSB do pino A0 flutuante |
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

#### Modelo de Ataques

Tentar resolver ainda

---

## Resultados

*Espaço reservado para inserção dos resultados experimentais após execução*


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
