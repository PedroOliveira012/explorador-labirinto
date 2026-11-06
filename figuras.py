"""
figuras.py - Gera as figuras do artigo (PDF vetorial + PNG) em resultados/
  fig_comparacao: BFS x DFS no MESMO labirinto (Pequeno)
  fig_ciclos:     comprimento do caminho x nº de ciclos (Médio)
"""
import os
import shutil
import statistics as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from grafo import grade_para_grafo, PAREDE
from algoritmos import bfs, dfs
from labirinto import gerar_labirinto, TAMANHOS
from experimento import rodar_config

plt.rcParams.update({"font.family": "serif", "font.size": 8})
COR = {"parede": "#1f2937", "livre": "#ffffff", "BFS": "#93c5fd", "DFS": "#fdba74",
       "caminho": "#f5b400", "entrada": "#16a34a", "saida": "#dc2626"}


def hexrgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def imagem(grade, res, s, e):
    img = np.array([[hexrgb(COR["parede"]) if v == PAREDE else hexrgb(COR["livre"]) for v in lin]
                    for lin in grade])
    for (l, c) in res.visitados:
        img[l, c] = hexrgb(COR[res.algoritmo])
    for (l, c) in res.caminho:
        img[l, c] = hexrgb(COR["caminho"])
    img[s] = hexrgb(COR["entrada"]); img[e] = hexrgb(COR["saida"])
    return img


def escolher_semente(lc, cc):
    """Escolhe, sem cherry-picking, o labirinto cuja razão DFS/BFS está mais
    próxima da média das 100 sementes do experimento."""
    razoes = []
    for sem in range(100):
        grade, s, e, _ = gerar_labirinto(lc, cc, 0.10, semente=sem)
        g = grade_para_grafo(grade)
        razoes.append(dfs(g, s, e).comprimento / bfs(g, s, e).comprimento)
    media = st.mean(razoes)
    return min(range(100), key=lambda i: abs(razoes[i] - media)), media


if __name__ == "__main__":
    os.makedirs("resultados", exist_ok=True)
    lc, cc = TAMANHOS["Pequeno"]
    sem, media = escolher_semente(lc, cc)
    grade, s, e, _ = gerar_labirinto(lc, cc, 0.10, semente=sem)
    g = grade_para_grafo(grade)
    rb, rd = bfs(g, s, e), dfs(g, s, e)
    print(f"Fig. 1: semente {sem} | BFS {rb.num_visitados} visit./{rb.comprimento} arestas | "
          f"DFS {rd.num_visitados} visit./{rd.comprimento} arestas | razão média do exp. = {media:.2f}")

    fig, eixos = plt.subplots(1, 2, figsize=(3.45, 1.95))
    for ax, r in zip(eixos, (rb, rd)):
        ax.imshow(imagem(grade, r, s, e), interpolation="nearest")
        ax.set_title(f"{r.algoritmo}: {r.num_visitados} visitados,\ncomprimento {r.comprimento}", fontsize=7)
        ax.axis("off")
    fig.subplots_adjust(top=0.80, bottom=0.02, left=0.02, right=0.98, wspace=0.06)
    fig.savefig("resultados/fig_comparacao.pdf"); fig.savefig("resultados/fig_comparacao.png", dpi=300)

    # Figura 2: efeito dos ciclos
    lc, cc = TAMANHOS["Médio"]
    xs, yb, yd = [], [], []
    for frac in (0.0, 0.02, 0.05, 0.10, 0.20):
        linhas = rodar_config(lc, cc, frac)
        xs.append(st.mean(l["ciclos"] for l in linhas))
        yb.append(st.mean(l["bfs_comp"] for l in linhas))
        yd.append(st.mean(l["dfs_comp"] for l in linhas))
    fig, ax = plt.subplots(figsize=(3.45, 2.2))
    ax.plot(xs, yd, "s--", color="#c2410c", label="DFS")
    ax.plot(xs, yb, "o-", color="#1d4ed8", label="BFS (mínimo)")
    ax.set_xlabel("Ciclos independentes no grafo")
    ax.set_ylabel("Comprimento médio do caminho\n(arestas)")
    ax.grid(alpha=0.3); ax.legend(frameon=False)
    fig.tight_layout(pad=0.4)
    fig.savefig("resultados/fig_ciclos.pdf"); fig.savefig("resultados/fig_ciclos.png", dpi=300)
    print("Fig. 2 gerada.")
    if os.path.isdir("artigo"):
        for nome in ("fig_comparacao.pdf", "fig_ciclos.pdf"):
            shutil.copy(os.path.join("resultados", nome), os.path.join("artigo", nome))
    print("Figuras copiadas para artigo/.")
