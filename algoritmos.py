"""
algoritmos.py - BFS e DFS sobre o grafo do labirinto (Etapa 4)

Este módulo NÃO desenha nada. Cada algoritmo devolve um ResultadoBusca com:
  - visitados: vértices na ORDEM em que foram explorados (a interface
               reproduz essa lista na animação)
  - caminho:   lista de vértices da entrada até a saída (ou None)
  - tempo:     segundos gastos

"""
from collections import deque
import time


class ResultadoBusca:
    """Guarda o que o relatório e a interface precisam de uma execução."""

    def __init__(self, algoritmo, visitados, caminho, tempo):
        self.algoritmo = algoritmo
        self.visitados = visitados
        self.caminho = caminho
        self.tempo = tempo

    @property
    def encontrou(self):
        return self.caminho is not None

    @property
    def num_visitados(self):
        return len(self.visitados)

    @property
    def comprimento(self):
        return len(self.caminho) - 1 if self.caminho else None


def reconstruir_caminho(pai, origem, destino):
    """
    Sai do destino e volta pelos 'pais' até a origem; depois inverte.
    Como cada vértice só é descoberto uma vez, o resultado nunca repete
    vértices: é um CAMINHO , e não só um passeio.
    """
    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(pai[caminho[-1]])
    caminho.reverse()
    return caminho


def bfs(grafo, origem, destino):
    """
    Busca em LARGURA: usa uma FILA (primeiro a entrar, primeiro a sair).
    Explora por níveis: distância 0, depois 1, depois 2...
    Em grafo sem pesos, o 1º caminho que chega ao destino é MÍNIMO.
    """
    inicio = time.perf_counter()
    fila = deque([origem])
    pai = {origem: None}      # também funciona como conjunto de "já descobertos"
    visitados = []            # ordem de exploração (para a animação)
    caminho = None

    while fila:
        v = fila.popleft()
        visitados.append(v)
        if v == destino:
            caminho = reconstruir_caminho(pai, origem, destino)
            break
        for w in grafo.vizinhos(v):
            if w not in pai:  # marca ao ENFILEIRAR: ninguém entra 2 vezes
                pai[w] = v
                fila.append(w)

    return ResultadoBusca("BFS", visitados, caminho, time.perf_counter() - inicio)


def dfs(grafo, origem, destino):
    """
    Busca em PROFUNDIDADE (versão iterativa): usa uma PILHA (LIFO).
    Segue um caminho até o fim; num beco sem saída, volta ao último
    ponto com alternativas (o 'backtracking' é o desempilhar).
    Acha UM caminho, não necessariamente o menor.
    """
    inicio = time.perf_counter()
    pilha = [(origem, None)]  # cada item: (vértice, quem o empilhou)
    pai = {}                  # só preenchido quando o vértice é VISITADO
    visitados = []
    caminho = None

    while pilha:
        v, de_quem = pilha.pop()
        if v in pai:          # já visitado por outro ramo: descarta
            continue
        pai[v] = de_quem      # marca ao DESEMPILHAR
        visitados.append(v)
        if v == destino:
            caminho = reconstruir_caminho(pai, origem, destino)
            break
        # Empilha em ORDEM INVERSA: como a pilha é LIFO, o 1º vizinho da
        # lista (cima) é o último a entrar e, portanto, o 1º a ser explorado.
        # Assim o DFS segue a ordem cima, direita, baixo, esquerda.
        for w in reversed(grafo.vizinhos(v)):
            if w not in pai:
                pilha.append((w, v))

    return ResultadoBusca("DFS", visitados, caminho, time.perf_counter() - inicio)


def eh_caminho_valido(grafo, seq):
    if len(seq) != len(set(seq)):
        return False
    return all(b in grafo.vizinhos(a) for a, b in zip(seq, seq[1:]))
