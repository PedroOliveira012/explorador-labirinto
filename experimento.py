"""
experimento.py - Experimento reprodutível BFS x DFS (Etapa 6)

Roda BFS e DFS em muitos labirintos (sementes fixas 0..N-1) e gera:
  resultados/por_labirinto.csv   dados brutos (1 linha por labirinto e tamanho)
  resultados/tabela_tamanhos.tex tabela LaTeX (efeito do tamanho)
  resultados/tabela_ciclos.tex   tabela LaTeX (efeito da quantidade de ciclos)
Execute:  python experimento.py
"""
import csv
import os
import shutil
import statistics as st
from grafo import grade_para_grafo
from algoritmos import bfs, dfs, eh_caminho_valido
from labirinto import gerar_labirinto, TAMANHOS

N = 100            # labirintos por configuração
REPETICOES = 5     # execuções por algoritmo para medir tempo (usa-se o mínimo)
FRACAO_PADRAO = 0.10


def medir(grafo, s, e):
    """Roda BFS e DFS; tempo = mínimo de REPETICOES execuções (reduz ruído)."""
    rb = min((bfs(grafo, s, e) for _ in range(REPETICOES)), key=lambda r: r.tempo)
    rd = min((dfs(grafo, s, e) for _ in range(REPETICOES)), key=lambda r: r.tempo)
    assert rb.encontrou and rd.encontrou
    assert eh_caminho_valido(grafo, rb.caminho) and eh_caminho_valido(grafo, rd.caminho)
    assert rb.comprimento <= rd.comprimento           # garantia teórica da BFS
    return rb, rd


def rodar_config(linhas_cel, colunas_cel, fracao):
    linhas = []
    for sem in range(N):
        grade, s, e, k = gerar_labirinto(linhas_cel, colunas_cel, fracao, semente=sem)
        g = grade_para_grafo(grade)
        rb, rd = medir(g, s, e)
        linhas.append(dict(
            semente=sem, V=g.num_vertices(), E=g.num_arestas(), ciclos=k,
            bfs_visit=rb.num_visitados, bfs_comp=rb.comprimento, bfs_ms=rb.tempo * 1000,
            dfs_visit=rd.num_visitados, dfs_comp=rd.comprimento, dfs_ms=rd.tempo * 1000))
    return linhas


def media_dp(xs):
    return st.mean(xs), st.stdev(xs)


def resumo(linhas):
    col = lambda k: [l[k] for l in linhas]
    return dict(
        V=st.mean(col("V")), E=st.mean(col("E")),
        bfs_visit=media_dp(col("bfs_visit")), dfs_visit=media_dp(col("dfs_visit")),
        bfs_comp=media_dp(col("bfs_comp")), dfs_comp=media_dp(col("dfs_comp")),
        bfs_ms=st.median(col("bfs_ms")), dfs_ms=st.median(col("dfs_ms")),
        razao_comp=st.mean(l["dfs_comp"] / l["bfs_comp"] for l in linhas),
        dfs_mais_longo=100 * sum(l["dfs_comp"] > l["bfs_comp"] for l in linhas) / len(linhas),
        dfs_menos_visit=100 * sum(l["dfs_visit"] < l["bfs_visit"] for l in linhas) / len(linhas),
    )


def br(texto):
    """Troca ponto por vírgula decimal (pt-BR) no LaTeX."""
    return texto.replace(".", "{,}")


def fmt(par):
    return br(f"{par[0]:.1f}") + " $\\pm$ " + br(f"{par[1]:.1f}")


def normalizar_linhas_tex(caminho):
    """
    Deixa o arquivo como linhas de tabela separadas por '\\ \\hline', com a
    ULTIMA linha sem terminador: o artigo a fecha com '\\ \\hline' depois do
    \\input. Isso evita um problema do LaTeX com \\input terminando em '\\\\'.
    """
    with open(caminho) as f:
        linhas = [l.rstrip("\n") for l in f if l.strip() and not l.startswith("%")]
    sufixo = " \\\\ \\hline"
    linhas = [l[:-len(sufixo)] if l.endswith(sufixo) else l for l in linhas]
    with open(caminho, "w") as f:
        f.write((sufixo + "\n").join(linhas) + "\n")


if __name__ == "__main__":
    os.makedirs("resultados", exist_ok=True)
    # ---------- Experimento 1: efeito do tamanho ----------
    todas, resumos = [], {}
    for nome, (lc, cc) in TAMANHOS.items():
        linhas = rodar_config(lc, cc, FRACAO_PADRAO)
        for l in linhas:
            l["tamanho"] = nome
        todas += linhas
        resumos[nome] = resumo(linhas)

    campos = ["tamanho", "semente", "V", "E", "ciclos", "bfs_visit", "bfs_comp", "bfs_ms",
              "dfs_visit", "dfs_comp", "dfs_ms"]
    with open("resultados/por_labirinto.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for l in todas:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in l.items() if k in campos})

    print(f"EXPERIMENTO 1 - efeito do tamanho ({N} labirintos por tamanho, {int(FRACAO_PADRAO*100)}% de paredes extras)")
    print(f"{'Tam.':8}{'|V|':>7}{'|E|':>7} | {'BFS visit.':>16}{'DFS visit.':>16} | {'BFS comp.':>14}{'DFS comp.':>14} | "
          f"{'DFS/BFS':>7} | {'DFS>':>5}{'DFS<vis':>8} | {'BFS ms':>7}{'DFS ms':>7}")
    for nome, r in resumos.items():
        print(f"{nome:8}{r['V']:7.0f}{r['E']:7.0f} | "
              f"{r['bfs_visit'][0]:9.1f}±{r['bfs_visit'][1]:5.1f}{r['dfs_visit'][0]:9.1f}±{r['dfs_visit'][1]:5.1f} | "
              f"{r['bfs_comp'][0]:7.1f}±{r['bfs_comp'][1]:4.1f}{r['dfs_comp'][0]:7.1f}±{r['dfs_comp'][1]:5.1f} | "
              f"{r['razao_comp']:7.2f} | {r['dfs_mais_longo']:4.0f}%{r['dfs_menos_visit']:7.0f}% | "
              f"{r['bfs_ms']:7.3f}{r['dfs_ms']:7.3f}")

    with open("resultados/tabela_tamanhos.tex", "w") as f:
        f.write("% gerado por experimento.py\n")
        for nome, r in resumos.items():
            f.write(f"{nome} & {r['V']:.0f} & {fmt(r['bfs_visit'])} & {fmt(r['dfs_visit'])} & "
                    f"{fmt(r['bfs_comp'])} & {fmt(r['dfs_comp'])} & {br(f'{r['razao_comp']:.2f}')} & "
                    f"{br(f'{r['bfs_ms']:.2f}')} & {br(f'{r['dfs_ms']:.2f}')} \\\\ \\hline\n")

    normalizar_linhas_tex("resultados/tabela_tamanhos.tex")

    # ---------- Experimento 2: efeito dos ciclos (tamanho Médio) ----------
    print(f"\nEXPERIMENTO 2 - efeito dos ciclos (Médio, {N} labirintos por linha)")
    print(f"{'Paredes extras':>14}{'Ciclos':>8} | {'BFS comp.':>10}{'DFS comp.':>10}{'DFS/BFS':>9} | {'DFS mais longo':>15}")
    lc, cc = TAMANHOS["Médio"]
    with open("resultados/tabela_ciclos.tex", "w") as f:
        f.write("% gerado por experimento.py\n")
        for frac in (0.0, 0.02, 0.05, 0.10, 0.20):
            linhas = rodar_config(lc, cc, frac)
            r = resumo(linhas)
            ciclos = st.mean(l["ciclos"] for l in linhas)
            print(f"{frac*100:13.0f}%{ciclos:8.0f} | {r['bfs_comp'][0]:10.1f}{r['dfs_comp'][0]:10.1f}"
                  f"{r['razao_comp']:9.2f} | {r['dfs_mais_longo']:14.0f}%")
            f.write(f"{frac*100:.0f}\\% & {ciclos:.0f} & {br(f'{r['bfs_comp'][0]:.1f}')} & {br(f'{r['dfs_comp'][0]:.1f}')} & "
                    f"{br(f'{r['razao_comp']:.2f}')} & {r['dfs_mais_longo']:.0f}\\% \\\\ \\hline\n")
    normalizar_linhas_tex("resultados/tabela_ciclos.tex")

    # Copia as tabelas para a pasta do artigo (se existir), para o LaTeX usar os números novos
    if os.path.isdir("artigo"):
        for nome in ("tabela_tamanhos.tex", "tabela_ciclos.tex"):
            shutil.copy(os.path.join("resultados", nome), os.path.join("artigo", nome))
    print("\nArquivos gerados em resultados/ (e copiados para artigo/).")
