"""
grafo.py - Representação do labirinto como grafo (Etapa 3)

Este módulo NÃO conhece interface gráfica nem algoritmos de busca.
Ele só responde a pergunta: "como transformar uma grade em G = (V, E)?"

"""

# Valores possíveis de cada célula da grade
LIVRE = 0
PAREDE = 1

# Ordem FIXA de exploração dos vizinhos: cima, direita, baixo, esquerda.
# Cada par é (delta_linha, delta_coluna). Manter a ordem fixa torna o
# DFS determinístico e permite reproduzir/explicar os resultados.
MOVIMENTOS = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class Grafo:
    """
    Grafo simples, não dirigido e não ponderado, guardado como
    LISTA DE ADJACÊNCIA.

    self.adj é um dicionário:  { vértice: [vizinho1, vizinho2, ...] }
    Aqui, cada vértice é uma tupla (linha, coluna) da grade.
    """

    def __init__(self):
        self.adj = {}

    # ---- construção --------------------------------------------------
    def adicionar_vertice(self, v):
        """Adiciona v a V (sem vizinhos ainda)."""
        if v not in self.adj:
            self.adj[v] = []

    def adicionar_aresta(self, u, v):
        """
        Adiciona a aresta (u, v) a E.
        Como o grafo é NÃO DIRIGIDO, a aresta conecta u a v e v a u
        
        Ignora laços (u == v) e arestas repetidas: o grafo é SIMPLES.
        """
        if u == v or v in self.adj[u]:
            return
        self.adj[u].append(v)
        self.adj[v].append(u)

    # ---- consultas ---------------------------------------------------
    def vertices(self):
        """Conjunto V."""
        return list(self.adj.keys())

    def vizinhos(self, v):
        """Vizinhos de v. É a operação que BFS e DFS mais usam."""
        return self.adj[v]

    def grau(self, v):
        """Grau de v: quantas arestas incidem nele """
        return len(self.adj[v])

    def num_vertices(self):
        """|V|"""
        return len(self.adj)

    def num_arestas(self):
        """
        |E|. Pela propriedade da soma dos graus, 2 x |E|,
        então |E| = (soma dos graus) / 2. Cada aresta é contada duas
        vezes na lista de adjacência (uma em cada extremo).
        """
        return sum(len(viz) for viz in self.adj.values()) // 2


def grade_para_grafo(grade):
    """
    Transforma a grade do labirinto em um Grafo.

    grade: lista de listas com LIVRE (0) ou PAREDE (1).

    Regra de modelagem:
      - célula livre   -> vértice (linha, coluna)
      - parede         -> nada (posição bloqueada)
      - duas livres vizinhas nas 4 direções -> aresta
    """
    g = Grafo()
    linhas = len(grade)
    colunas = len(grade[0]) if linhas else 0

    # 1) Vértices: toda célula livre vira um vértice.
    for l in range(linhas):
        for c in range(colunas):
            if grade[l][c] == LIVRE:
                g.adicionar_vertice((l, c))

    # 2) Arestas: para cada vértice, olha os 4 vizinhos NA ORDEM FIXA.
    #    Isso garante que cada lista de adjacência já fique em
    #    cima, direita, baixo, esquerda.
    #    A simetria é natural: se (l,c) enxerga (l,c+1), então
    #    (l,c+1) também enxerga (l,c) quando for processado.
    for (l, c) in g.vertices():
        for dl, dc in MOVIMENTOS:
            nl, nc = l + dl, c + dc
            dentro = 0 <= nl < linhas and 0 <= nc < colunas
            if dentro and grade[nl][nc] == LIVRE:
                if (nl, nc) not in g.adj[(l, c)]:
                    g.adj[(l, c)].append((nl, nc))
    return g
