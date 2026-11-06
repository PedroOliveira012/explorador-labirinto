"""teste_etapa4.py - Valida BFS e DFS em labirintos de teste."""
from grafo import grade_para_grafo
from algoritmos import bfs, dfs, eh_caminho_valido
from teste_etapa3 import ler_texto

LABIRINTOS = {
 "A: árvore (1 só caminho)": """
#########
#S..#...#
#.#.#.#.#
#.#...#E#
#########
""",
 "B: 1 ciclo, 2 rotas iguais": """
#######
#S....#
#.###.#
#....E#
#######
""",
 "D: DFS dá a volta longa": """
#########
#S......#
#E#####.#
#.......#
#########
""",
 "E: SEM solução (desconexo)": """
#######
#S.#.E#
#######
""",
}

def todos_caminhos(g, atual, destino, vistos, acc):
    """Força bruta: enumera TODOS os caminhos simples (só p/ labirintos minúsculos)."""
    if atual == destino:
        acc.append(len(vistos) - 1); return
    for w in g.vizinhos(atual):
        if w not in vistos:
            vistos.append(w); todos_caminhos(g, w, destino, vistos, acc); vistos.pop()

for nome, texto in LABIRINTOS.items():
    grade, s, e = ler_texto(texto)
    g = grade_para_grafo(grade)
    print(f"=== {nome} | |V|={g.num_vertices()} ===")
    rb, rd = bfs(g, s, e), dfs(g, s, e)
    for r in (rb, rd):
        if r.encontrou:
            assert eh_caminho_valido(g, r.caminho)
            assert r.caminho[0] == s and r.caminho[-1] == e
            print(f"{r.algoritmo}: visitados={r.num_visitados:2d}  comprimento={r.comprimento:2d}")
        else:
            print(f"{r.algoritmo}: visitados={r.num_visitados:2d}  SEM CAMINHO")
        assert len(set(r.visitados)) == len(r.visitados)  # ninguém visitado 2x
    # BFS e DFS concordam sobre existir ou não solução
    assert rb.encontrou == rd.encontrou
    if rb.encontrou:
        # Confere a garantia da BFS contra força bruta
        acc = []; todos_caminhos(g, s, e, [s], acc)
        assert rb.comprimento == min(acc), "BFS deveria achar o mínimo!"
        assert rd.comprimento >= rb.comprimento
        print(f"Menor comprimento (força bruta) = {min(acc)}  -> BFS confere; DFS {'= mínimo' if rd.comprimento == min(acc) else 'MAIOR que o mínimo'}")
    print()
print("Todos os testes passaram.")
