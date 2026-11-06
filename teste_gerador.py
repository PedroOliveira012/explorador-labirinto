"""teste_gerador.py - Valida o gerador e mostra BFS x DFS nos 3 tamanhos."""
from grafo import grade_para_grafo
from algoritmos import bfs, dfs, eh_caminho_valido
from labirinto import gerar_labirinto, grade_para_texto, TAMANHOS

def conexo(g, origem):
    visto, pilha = {origem}, [origem]
    while pilha:
        v = pilha.pop()
        for w in g.vizinhos(v):
            if w not in visto:
                visto.add(w); pilha.append(w)
    return len(visto) == g.num_vertices()

if __name__ == "__main__":
    # Exemplo visual: labirinto pequeno
    grade, s, e, k = gerar_labirinto(5, 8, fracao_ciclos=0.1, semente=3)
    print("Exemplo (5x8 células, semente 3):")
    print(grade_para_texto(grade, s, e)); print()

    # 1) Árvore pura: |E| = |V|-1 e conexo
    for sem in range(10):
        grade, s, e, k = gerar_labirinto(10, 10, fracao_ciclos=0, semente=sem)
        g = grade_para_grafo(grade)
        assert k == 0 and conexo(g, s) and g.num_arestas() == g.num_vertices() - 1
    print("OK: fração 0 gera árvore (conexa, |E| = |V|-1) em 10 sementes.")

    # 2) Com ciclos: continua conexo e |E| - (|V|-1) = nº de paredes removidas
    for nome, (lc, cc) in TAMANHOS.items():
        for sem in range(10):
            grade, s, e, k = gerar_labirinto(lc, cc, semente=sem)
            g = grade_para_grafo(grade)
            assert conexo(g, s) and e in g.adj
            assert g.num_arestas() - (g.num_vertices() - 1) == k
            # cada posição livre da grade é um vértice (células + corredores)
            livres = sum(v == 0 for linha in grade for v in linha)
            assert g.num_vertices() == livres
    print("OK: com ciclos, continua conexo e ciclos independentes = paredes removidas.\n")

    # 3) Comparação BFS x DFS: 30 labirintos por tamanho
    print(f"{'Tamanho':8} | {'BFS visit.':>10} {'BFS comp.':>9} | {'DFS visit.':>10} {'DFS comp.':>9} | DFS mais longo em")
    for nome, (lc, cc) in TAMANHOS.items():
        N = 30; sv = {"b": 0, "d": 0}; sc = {"b": 0, "d": 0}; piores = 0
        for sem in range(N):
            grade, s, e, k = gerar_labirinto(lc, cc, semente=sem)
            g = grade_para_grafo(grade)
            rb, rd = bfs(g, s, e), dfs(g, s, e)
            assert rb.encontrou and rd.encontrou
            assert eh_caminho_valido(g, rb.caminho) and eh_caminho_valido(g, rd.caminho)
            assert rb.comprimento <= rd.comprimento
            sv["b"] += rb.num_visitados; sv["d"] += rd.num_visitados
            sc["b"] += rb.comprimento;  sc["d"] += rd.comprimento
            piores += rd.comprimento > rb.comprimento
        print(f"{nome:8} | {sv['b']/N:10.1f} {sc['b']/N:9.1f} | {sv['d']/N:10.1f} {sc['d']/N:9.1f} | {piores}/{N}")
    print("\nTodos os testes passaram.")
