# Torre de Hanói - Visualizador Gráfico

Um visualizador interativo e moderno para o clássico problema matemático da Torre de Hanói, desenvolvido em Python utilizando `tkinter`. O projeto demonstra a aplicação de algoritmos recursivos com uma interface gráfica animada e responsiva.

## Sobre o Projeto

Este projeto permite que o usuário configure o número de discos, ajuste a velocidade da animação e visualize o passo a passo da solução ótima.

### Principais Funcionalidades

* **Solução Automática:** Implementação visual do algoritmo recursivo clássico.
* **Configuração Dinâmica:** Suporte para 3 a 10 discos.
* **Controle de Velocidade:** Ajuste em tempo real da velocidade da animação (de lento a instantâneo).
* **Interface Moderna:** Design inspirado no tema *Nord*, com painéis arredondados e cores suaves.
* **Animações Suaves:** Movimentação fluida dos discos utilizando vetores e funções de suavização (*easing*).
* **Estatísticas:** Contador de movimentos em tempo real comparado com o mínimo matemático necessário ($2^n - 1$).
* **Arquitetura Desacoplada:** Uso de Event Bus para comunicação entre lógica e interface.

## Tecnologias Utilizadas

* **Python 3.x**
* **Tkinter:** Para a interface gráfica (GUI) e Canvas.
* **Threading:** Para executar o algoritmo de solução sem travar a interface.
* **Math:** Para cálculos de vetores e interpolação linear.

## Estrutura do Projeto

O código foi organizado seguindo princípios de separação de responsabilidades:

| Arquivo | Descrição |
| :--- | :--- |
| `main.py` | **Ponto de entrada**. Inicializa a janela, configura o layout e conecta os componentes. |
| `engine.py` | Contém o `GameEngine` (regras do jogo) e o `HanoiSolver` (algoritmo recursivo). |
| `renderer.py` | Gerencia o desenho no Canvas e as animações quadro a quadro dos discos. |
| `events.py` | Implementa um **Event Bus** (Padrão Observer) para gerenciar eventos globais. |
| `models.py` | Definição das classes de dados: `Disk`, `Peg` (Pino) e `MoveCommand`. |
| `ui_components.py` | Componentes visuais customizados (Botões modernos, Painéis arredondados). |
| `config.py` | Constantes globais, configurações de cores (Tema Nord) e textos. |
| `utils.py` | Utilitários matemáticos (`Vector2D`, `Lerp`, `Easing`) para a física da animação. |

## Como Rodar

### Pré-requisitos
Certifique-se de ter o **Python 3** instalado em sua máquina. O projeto utiliza apenas bibliotecas padrão do Python, então não é necessário instalar pacotes via `pip` (como pandas ou numpy).

> **Nota para usuários Linux:** Em algumas distribuições, o `tkinter` deve ser instalado separadamente:
> `sudo apt-get install python3-tk`

### Executando

1. Clone o repositório ou baixe os arquivos:

```bash

   git clone https://github.com/therjyer/Projeto_Final_Matematica_Discreta

```

2. Entre na pasta do projeto:

```bash

   cd Projeto_Final_Matematica_Discreta

```

3. Execute o arquivo principal:

```bash

    python main.py

```



## Como Funciona (Lógica)

### O Algoritmo

O núcleo da solução está na classe `HanoiSolver` (`engine.py`). Utilizamos a recursão clássica:

1. Mover  discos da **Origem** para o **Auxiliar**.
2. Mover o disco maior da **Origem** para o **Destino**.
3. Mover  discos do **Auxiliar** para o **Destino**.

### As Animações

Diferente de scripts simples de console, este projeto usa uma *Thread* separada para calcular os movimentos. Quando um movimento é decidido, um evento é disparado. O `renderer.py` intercepta esse evento e calcula a trajetória visual usando interpolação (Lerp) e vetores 2D (`utils.py`), criando uma transição suave entre os pinos.

## Design

A interface utiliza a paleta de cores **Nord**:

* Fundo: `#2E3440`
* Painéis: `#3B4252`
* Acentos: `#88C0D0`, `#5E81AC`
* Discos: Cores variadas (`#BF616A`, `#D08770`, `#EBCB8B`, etc.)

---