"""
teste_etapa3.py - Valida a conversão labirinto -> grafo.
Os labirintos são desenhados em texto: # parede, . livre, S entrada, E saída.
"""
from grafo import grade_para_grafo, LIVRE, PAREDE

def ler_texto(texto):
    grade, entrada, saida = [], None, None
    for l, linha in enumerate(texto.strip("\n").split("\n")):
        linha_grade = []
        for c, ch in enumerate(linha):
            if ch == "S": entrada = (l, c)
            if ch == "E": saida = (l, c)
            linha_grade.append(PAREDE if ch == "#" else LIVRE)
        grade.append(linha_grade)
    return grade, entrada, saida

def conexo(g, origem):
    """Verificação provisória de conectividade (a BFS real vem na Etapa 4)."""
    visto, pilha = {origem}, [origem]
    while pilha:
        v = pilha.pop()
        for w in g.vizinhos(v):
            if w not in visto:
                visto.add(w); pilha.append(w)
    return len(visto) == g.num_vertices()

LABIRINTOS = {
 "A (sem ciclos)": """
#########
#S..#...#
#.#.#.#.#
#.#...#E#
#########
""",
 "B (com 1 ciclo)": """
#######
#S....#
#.###.#
#....E#
#######
""",
}

if __name__ == "__main__":
    for nome, texto in LABIRINTOS.items():
        grade, s, e = ler_texto(texto)
        g = grade_para_grafo(grade)
        n, m = g.num_vertices(), g.num_arestas()
        print(f"--- Labirinto {nome} ---")
        print(f"|V| = {n}   |E| = {m}   entrada = {s}   saída = {e}")

        assert sum(g.grau(v) for v in g.vertices()) == 2 * m
        # Grafo não dirigido: toda aresta existe nos dois sentidos
        for v in g.vertices():
            for w in g.vizinhos(v):
                assert v in g.vizinhos(w)
        # Paredes nunca são vértices; entrada e saída são vértices
        assert all(grade[l][c] == LIVRE for (l, c) in g.vertices())
        assert s in g.adj and e in g.adj
        # Todo vértice tem no máximo 4 vizinhos (4 direções)
        assert max(g.grau(v) for v in g.vertices()) <= 4

        ok = conexo(g, s)
        print(f"Conexo? {ok}")
        if ok:
            print("Árvore (n-1 arestas)?", m == n - 1, "| arestas além de n-1 (ciclos independentes):", m - (n - 1))
        print("Vizinhos da entrada (cima, direita, baixo, esquerda):", g.vizinhos(s))
        print()
    print("Todos os testes passaram.")
