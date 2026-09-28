# Avaliação Experimental de Agentes Inteligentes - UECE

**Disciplina:** Inteligência Computacional
**Professor:** Gustavo Augusto Lima de Campos

**Alunos:**

* Lyanderson Silva Rodrigues
* Ismael Sousa Fonteles de Castro

---

## Objetivos

Este projeto tem como objetivo implementar e avaliar experimentalmente diferentes tipos de agentes inteligentes no ambiente do **Mundo do Aspirador de Pó (Vacuum World)**.

Foram implementados dois agentes:

* **Agente Reativo Simples**
* **Agente Reativo Baseado em Modelos**

A aplicação permite observar o comportamento dos agentes em uma matriz com células limpas, sujas e obstáculos, além de analisar seu desempenho utilizando diferentes medidas de desempenho.

Também foi desenvolvida uma simulação experimental com múltiplos ambientes aleatórios, permitindo comparar o comportamento dos agentes em diferentes condições.

---

## Tecnologias

O projeto foi desenvolvido utilizando:

* **Python 3**
* **Tkinter** — desenvolvimento da interface gráfica;
* **Pillow (PIL)** — carregamento e exibição da imagem do agente;
* **Matplotlib** — geração dos gráficos de desempenho;
* **Random** — geração dos ambientes e posições aleatórias;
* **Collections / deque** — utilizada na busca em largura (BFS) do agente baseado em modelos.

As bibliotecas externas utilizadas pelo projeto são:

```text
Pillow
matplotlib
```

O projeto utiliza um ambiente virtual Python (`venv`) para isolamento das dependências.

---

## Arquitetura

O projeto está organizado nos seguintes arquivos:

```text
.
├── agente_simples.py
├── agente_modelo.py
├── main.py
├── simulacao.py
├── requirements.txt
├── venv/
└── aspira_agent.png
```

### `agente_simples.py`

Implementa o **Agente Reativo Simples**.

O agente utiliza exclusivamente as informações recebidas pelos sensores no estado atual do ambiente. Sua principal regra é:

* Se a posição atual estiver suja → **Aspirar**;
* Caso contrário → movimentar-se pela matriz seguindo uma estratégia de varredura.

O agente mantém informações de direção e modo de movimentação para percorrer o ambiente.

---

### `agente_modelo.py`

Implementa o **Agente Reativo Baseado em Modelos**.

Diferentemente do agente reativo simples, este agente mantém uma representação interna do ambiente, armazenando informações sobre:

* posições conhecidas;
* posições limpas;
* posições sujas;
* obstáculos;
* posições ainda desconhecidas.

O agente utiliza essas informações para atualizar seu **modelo interno do ambiente** e planejar seus movimentos.

## Para encontrar caminhos até regiões desconhecidas ou sujas, é utilizada uma busca em largura (**BFS - Breadth-First Search**).

### `main.py`

É o programa principal da **interface gráfica interativa**.

A interface permite:

* selecionar o tipo de agente;
* executar a simulação passo a passo;
* executar a simulação automaticamente;
* definir a quantidade máxima de passos;
* definir a quantidade de obstáculos;
* reiniciar o ambiente;
* visualizar a posição do agente;
* acompanhar as medidas de desempenho.

O ambiente utilizado pela interface possui uma matriz **5 × 5** e os ambientes são gerados aleatoriamente.

A aplicação apresenta duas medidas de desempenho:

### Medida 1

Cada célula suja aspirada acrescenta **+1 ponto**.

```text
M1 = pontos por sujeira aspirada
```

### Medida 2

Considera tanto a limpeza quanto o custo dos movimentos:

```text
M2 = pontos por sujeira aspirada - custo dos movimentos
```

Na implementação, aspirar uma sujeira gera `+1` e cada movimento possui custo `-1`.

---

### `simulacao.py`

Responsável pela **avaliação experimental dos agentes**.

O programa gera ambientes aleatórios e executa os dois agentes em condições equivalentes, coletando os resultados para posterior comparação.

A configuração experimental utiliza:

* Matriz: **5 × 5**
* Ambientes por configuração: **1000**
* Obstáculos: **3**
* Limite de passos analisado: **25 a 60**

Esses parâmetros estão definidos diretamente no arquivo de simulação.
Durante os experimentos são coletadas informações sobre:

* desempenho pela Medida 1;
* desempenho pela Medida 2;
* desempenho em função da quantidade de passos;
* desempenho em função da quantidade inicial de sujeira;
* melhores resultados obtidos;
* piores resultados obtidos.

## O programa também gera gráficos para visualizar os resultados experimentais e apresenta os ambientes associados aos melhores e piores resultados de cada agente.

## Como executar

### 1. Clonar o projeto

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
```

### 2. Criar o ambiente virtual

Caso o ambiente virtual ainda não exista:

```bash
python3 -m venv venv
```

### 3. Ativar o ambiente virtual

No Linux/macOS:

```bash
source venv/bin/activate
```

No Windows:

```powershell
venv\Scripts\activate
```

### 4. Instalar as dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

As principais dependências do projeto são:

```text
Pillow
matplotlib
```

### 5. Executar a interface interativa

Para executar a aplicação principal:

```bash
python main.py
```

A interface gráfica será aberta e permitirá selecionar o agente e executar a simulação passo a passo ou automaticamente.

---

## Executando a avaliação experimental

Para executar a avaliação com múltiplos ambientes:

```bash
python simulacao.py
```

O programa executará os experimentos e, ao final, apresentará uma interface contendo os resultados.

São apresentados gráficos relacionados a:

* **Medida 1 × quantidade de passos**;
* **Medida 2 × quantidade de passos**;
* **Medida 1 × quantidade inicial de sujeira**;
* **Medida 2 × quantidade inicial de sujeira**.

Também são apresentadas as configurações correspondentes aos melhores e piores resultados de cada agente segundo a **Medida 2**.

