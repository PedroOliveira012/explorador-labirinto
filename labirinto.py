"""
labirinto.py - Gerador de labirintos (passo entre as Etapas 4 e 5)

Gera uma grade (lista de listas com LIVRE/PAREDE) pronta para ser
transformada em grafo por grafo.grade_para_grafo().

"""
import random
from grafo import LIVRE, PAREDE

# Tamanhos oferecidos ao usuário: (linhas de células, colunas de células)
TAMANHOS = {
    "Pequeno": (10, 10),
    "Médio": (20, 20),
    "Grande": (30, 30),
}


def gerar_labirinto(linhas_cel, colunas_cel, fracao_ciclos=0.10, semente=None):
    """
    Devolve (grade, entrada, saida, ciclos_criados).

    linhas_cel, colunas_cel : tamanho em CÉLULAS. A grade tem 2n+1 posições
                              por lado (células nas posições ímpares).
    fracao_ciclos           : paredes extras removidas, como fração do nº de
                              células. 0 gera uma árvore (um único caminho).
    semente                 : torna o labirinto reproduzível (útil em testes
                              e para comparar BFS x DFS no mesmo labirinto).
    """
    rng = random.Random(semente)
    linhas, colunas = 2 * linhas_cel + 1, 2 * colunas_cel + 1
    grade = [[PAREDE] * colunas for _ in range(linhas)]

    # --- Passo 1: labirinto perfeito (árvore) por backtracking iterativo ---
    inicio = (1, 1)
    grade[1][1] = LIVRE
    pilha = [inicio]
    while pilha:
        l, c = pilha[-1]
        # vizinhos a 2 passos (células) ainda não escavados
        candidatos = []
        for dl, dc in [(-2, 0), (0, 2), (2, 0), (0, -2)]:
            nl, nc = l + dl, c + dc
            if 1 <= nl < linhas - 1 and 1 <= nc < colunas - 1 and grade[nl][nc] == PAREDE:
                candidatos.append((nl, nc, dl, dc))
        if candidatos:
            nl, nc, dl, dc = rng.choice(candidatos)
            grade[l + dl // 2][c + dc // 2] = LIVRE   # derruba a parede entre as células
            grade[nl][nc] = LIVRE
            pilha.append((nl, nc))
        else:
            pilha.pop()                               # beco sem saída: volta

    # --- Passo 2: remove paredes extras para criar ciclos ---
    # Candidata = parede ENTRE duas células (l+c ímpar), dentro da borda.
    paredes = [(l, c) for l in range(1, linhas - 1) for c in range(1, colunas - 1)
               if (l + c) % 2 == 1 and grade[l][c] == PAREDE]
    qtd = min(len(paredes), round(fracao_ciclos * linhas_cel * colunas_cel))
    for (l, c) in rng.sample(paredes, qtd):
        grade[l][c] = LIVRE

    entrada = (1, 1)
    saida = (linhas - 2, colunas - 2)
    return grade, entrada, saida, qtd


def grade_para_texto(grade, entrada=None, saida=None):
    """Desenho em texto (# parede, espaço livre, S entrada, E saída)."""
    linhas = []
    for l, linha in enumerate(grade):
        s = ""
        for c, v in enumerate(linha):
            s += "S" if (l, c) == entrada else "E" if (l, c) == saida else ("#" if v == PAREDE else " ")
        linhas.append(s)
    return "\n".join(linhas)
