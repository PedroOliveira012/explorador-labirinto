"""
interface.py - Interface gráfica em Tkinter (Etapa 5)

A interface NÃO implementa nenhum algoritmo de grafos. Ela apenas:
  1) chama gerar_labirinto() e grade_para_grafo();
  2) chama bfs()/dfs() e recebe um ResultadoBusca;
  3) REPRODUZ a lista 'visitados' e o 'caminho' na tela, aos poucos,
     usando after() (animação) e mostra as métricas.

Assim a Teoria dos Grafos (grafo.py, algoritmos.py) fica separada da
visualização, e os mesmos dados alimentam a animação e a comparação.
"""
import tkinter as tk
from tkinter import ttk

from grafo import grade_para_grafo, LIVRE
from algoritmos import bfs, dfs
from labirinto import gerar_labirinto, TAMANHOS

TAM_CANVAS = 640        # lado do Canvas em pixels
ATRASO_MS = 20          # intervalo entre quadros da animação

# Paleta de cores
COR_PAREDE = "#1f2937"
COR_LIVRE = "#ffffff"
COR_ENTRADA = "#16a34a"
COR_SAIDA = "#dc2626"
COR_CAMINHO = "#f5b400"
COR_VISITADO = {"BFS": "#93c5fd", "DFS": "#fdba74"}   # azul = BFS, laranja = DFS

ALGORITMOS = {"BFS": bfs, "DFS": dfs}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Explorador de Labirintos - BFS x DFS (Grupo 10)")
        self.resizable(False, False)

        self.grade = self.grafo = None
        self.entrada = self.saida = None
        self.ids = {}                 # (linha, coluna) -> id do retângulo no Canvas
        self.resultados = {}          # "BFS"/"DFS" -> ResultadoBusca do labirinto atual
        self._job = None              # id do after() pendente (para poder cancelar)
        self.rodando = False

        self._montar_widgets()
        self.novo_labirinto()

    # ------------------------------------------------------------------
    # Montagem da janela
    # ------------------------------------------------------------------
    def _montar_widgets(self):
        topo = ttk.Frame(self, padding=(10, 10, 10, 4))
        topo.pack(fill="x")

        ttk.Label(topo, text="Tamanho:").pack(side="left")
        self.var_tamanho = tk.StringVar(value="Médio")
        self.combo = ttk.Combobox(topo, textvariable=self.var_tamanho, width=9,
                                  values=list(TAMANHOS), state="readonly")
        self.combo.pack(side="left", padx=(4, 6))
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.novo_labirinto())

        self.btn_novo = ttk.Button(topo, text="Novo labirinto", command=self.novo_labirinto)
        self.btn_novo.pack(side="left", padx=4)
        self.btn_bfs = ttk.Button(topo, text="Executar BFS", command=lambda: self.executar("BFS"))
        self.btn_bfs.pack(side="left", padx=(16, 4))
        self.btn_dfs = ttk.Button(topo, text="Executar DFS", command=lambda: self.executar("DFS"))
        self.btn_dfs.pack(side="left", padx=4)
        self.btn_limpar = ttk.Button(topo, text="Limpar", command=self.limpar)
        self.btn_limpar.pack(side="left", padx=4)

        vel = ttk.Frame(self, padding=(10, 0, 10, 6))
        vel.pack(fill="x")
        ttk.Label(vel, text="Velocidade:  lenta").pack(side="left")
        self.vel = tk.Scale(vel, from_=1, to=10, orient="horizontal", length=220,
                            showvalue=False)
        self.vel.set(5)
        self.vel.pack(side="left", padx=4)
        ttk.Label(vel, text="rápida").pack(side="left")

        corpo = ttk.Frame(self, padding=(10, 0, 10, 10))
        corpo.pack()

        self.canvas = tk.Canvas(corpo, width=TAM_CANVAS, height=TAM_CANVAS,
                                bg=COR_PAREDE, highlightthickness=0)
        self.canvas.pack(side="left")

        lateral = ttk.Frame(corpo, padding=(12, 0, 0, 0))
        lateral.pack(side="left", fill="y")
        self._montar_lateral(lateral)

    def _montar_lateral(self, pai):
        g = ttk.LabelFrame(pai, text="Grafo do labirinto", padding=8)
        g.pack(fill="x")
        self.var_grafo = tk.StringVar()
        ttk.Label(g, textvariable=self.var_grafo, justify="left").pack(anchor="w")

        # --- Tabela de resultados ---
        r = ttk.LabelFrame(pai, text="Resultados", padding=8)
        r.pack(fill="x", pady=8)
        self.var = {}
        for col, alg in enumerate(("BFS", "DFS"), start=1):
            tk.Label(r, text=alg, bg=COR_VISITADO[alg], width=10,
                     font=("TkDefaultFont", 10, "bold")).grid(row=0, column=col, padx=3, pady=(0, 4))
        campos = [("visitados", "Visitados"), ("comprimento", "Comprimento"), ("tempo", "Tempo")]
        for i, (chave, rotulo) in enumerate(campos, start=1):
            ttk.Label(r, text=rotulo).grid(row=i, column=0, sticky="w", pady=2)
            for col, alg in enumerate(("BFS", "DFS"), start=1):
                self.var[(alg, chave)] = tk.StringVar(value="—")
                ttk.Label(r, textvariable=self.var[(alg, chave)], width=11,
                          anchor="center").grid(row=i, column=col)
        ttk.Label(r, text="Comprimento = nº de arestas.\nTempo medido só no algoritmo,\nsem a animação.",
                  foreground="#6b7280", justify="left").grid(row=4, column=0, columnspan=3,
                                                              sticky="w", pady=(6, 0))

        # --- Comparação ---
        c = ttk.LabelFrame(pai, text="Comparação", padding=8)
        c.pack(fill="x")
        self.var_comp = tk.StringVar()
        ttk.Label(c, textvariable=self.var_comp, wraplength=250, justify="left").pack(anchor="w")

        # --- Legenda ---
        l = ttk.LabelFrame(pai, text="Legenda", padding=8)
        l.pack(fill="x", pady=8)
        itens = [(COR_ENTRADA, "Entrada"), (COR_SAIDA, "Saída"),
                 (COR_VISITADO["BFS"], "Visitado pela BFS"),
                 (COR_VISITADO["DFS"], "Visitado pelo DFS"),
                 (COR_CAMINHO, "Caminho encontrado"), (COR_PAREDE, "Parede")]
        for i, (cor, texto) in enumerate(itens):
            tk.Label(l, bg=cor, width=2, relief="solid", borderwidth=1).grid(row=i, column=0, pady=1)
            ttk.Label(l, text=texto).grid(row=i, column=1, sticky="w", padx=6)

    # ------------------------------------------------------------------
    # Labirinto e desenho
    # ------------------------------------------------------------------
    def novo_labirinto(self):
        self._cancelar_animacao()
        lc, cc = TAMANHOS[self.var_tamanho.get()]
        self.grade, self.entrada, self.saida, _ = gerar_labirinto(lc, cc)
        self.grafo = grade_para_grafo(self.grade)          # labirinto -> G = (V, E)

        n, m = self.grafo.num_vertices(), self.grafo.num_arestas()
        self.var_grafo.set(f"Vértices |V| = {n}\nArestas |E| = {m}\n"
                           f"Arestas além de |V|−1 = {m - (n - 1)}\n"
                           f"(cada uma cria um ciclo)")
        self._desenhar()
        self._zerar_resultados()
        self._set_rodando(False)

    def _desenhar(self):
        self.canvas.delete("all")
        self.ids = {}
        linhas, colunas = len(self.grade), len(self.grade[0])
        t = TAM_CANVAS // max(linhas, colunas)             # lado de cada quadrado
        deslocx = (TAM_CANVAS - t * colunas) // 2
        deslocy = (TAM_CANVAS - t * linhas) // 2
        for l in range(linhas):
            for c in range(colunas):
                if self.grade[l][c] == LIVRE:              # só posições livres (vértices)
                    x, y = deslocx + c * t, deslocy + l * t
                    self.ids[(l, c)] = self.canvas.create_rectangle(
                        x, y, x + t, y + t, fill=COR_LIVRE, outline="")
        self._pintar_extremos()

    def _pintar_extremos(self):
        self.canvas.itemconfig(self.ids[self.entrada], fill=COR_ENTRADA)
        self.canvas.itemconfig(self.ids[self.saida], fill=COR_SAIDA)

    def _pintar(self, v, cor):
        """Pinta um vértice, preservando as cores de entrada e saída."""
        if v != self.entrada and v != self.saida:
            self.canvas.itemconfig(self.ids[v], fill=cor)

    def _limpar_exploracao(self):
        for v in self.ids:
            self.canvas.itemconfig(self.ids[v], fill=COR_LIVRE)
        self._pintar_extremos()

    def _zerar_resultados(self):
        self.resultados = {}
        for chave in self.var:
            self.var[chave].set("—")
        self.var_comp.set("Execute BFS e DFS no mesmo\nlabirinto para comparar.")

    # ------------------------------------------------------------------
    # Execução e animação
    # ------------------------------------------------------------------
    def executar(self, nome):
        """Roda o algoritmo (instantâneo) e depois anima o resultado."""
        self._limpar_exploracao()
        self.resultados.pop(nome, None)
        for campo in ("visitados", "comprimento", "tempo"):
            self.var[(nome, campo)].set("—")
        self._atualizar_comparacao()

        res = ALGORITMOS[nome](self.grafo, self.entrada, self.saida)
        self._set_rodando(True)
        self._passo_visita(res, 0)

    def _passos_por_quadro(self):
        """Velocidade 1..10 -> 1, 2, 4, ..., 512 vértices pintados por quadro."""
        return 2 ** (int(self.vel.get()) - 1)

    def _passo_visita(self, res, i):
        fim = min(i + self._passos_por_quadro(), len(res.visitados))
        for v in res.visitados[i:fim]:
            self._pintar(v, COR_VISITADO[res.algoritmo])
        self.var[(res.algoritmo, "visitados")].set(str(fim))   # contador ao vivo
        if fim < len(res.visitados):
            self._job = self.after(ATRASO_MS, self._passo_visita, res, fim)
        else:
            self._passo_caminho(res, 0)

    def _passo_caminho(self, res, i):
        if res.caminho is None:                                # sem solução
            self._finalizar(res)
            return
        passo = max(1, self._passos_por_quadro() // 4)
        fim = min(i + passo, len(res.caminho))
        for v in res.caminho[i:fim]:
            self._pintar(v, COR_CAMINHO)
        if fim < len(res.caminho):
            self._job = self.after(ATRASO_MS, self._passo_caminho, res, fim)
        else:
            self._finalizar(res)

    def _finalizar(self, res):
        self._job = None
        self.resultados[res.algoritmo] = res
        n = res.algoritmo
        self.var[(n, "visitados")].set(str(res.num_visitados))
        self.var[(n, "comprimento")].set(str(res.comprimento) if res.encontrou else "sem caminho")
        self.var[(n, "tempo")].set(f"{res.tempo * 1000:.3f} ms")
        self._atualizar_comparacao()
        self._set_rodando(False)

    def _atualizar_comparacao(self):
        if "BFS" not in self.resultados or "DFS" not in self.resultados:
            self.var_comp.set("Execute BFS e DFS no mesmo\nlabirinto para comparar.")
            return
        b, d = self.resultados["BFS"], self.resultados["DFS"]
        linhas = []
        if b.encontrou and d.encontrou:
            dif = d.comprimento - b.comprimento
            if dif == 0:
                linhas.append(f"Caminho: os dois acharam {b.comprimento} arestas "
                              f"(o mínimo, garantido pela BFS).")
            else:
                linhas.append(f"Caminho: o DFS achou {d.comprimento} arestas, "
                              f"{dif} a mais que o mínimo ({b.comprimento}) da BFS.")
        dv = d.num_visitados - b.num_visitados
        if dv < 0:
            linhas.append(f"Exploração: o DFS visitou {-dv} vértices a menos que a BFS.")
        elif dv > 0:
            linhas.append(f"Exploração: o DFS visitou {dv} vértices a mais que a BFS.")
        else:
            linhas.append("Exploração: os dois visitaram a mesma quantidade.")
        self.var_comp.set("\n".join(linhas))

    # ------------------------------------------------------------------
    # Controles
    # ------------------------------------------------------------------
    def limpar(self):
        """Cancela a animação, limpa a exploração e os resultados (mesmo labirinto)."""
        self._cancelar_animacao()
        self._limpar_exploracao()
        self._zerar_resultados()
        self._set_rodando(False)

    def _cancelar_animacao(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

    def _set_rodando(self, rodando):
        self.rodando = rodando
        estado = "disabled" if rodando else "normal"
        for w in (self.btn_bfs, self.btn_dfs, self.btn_novo):
            w.config(state=estado)
        self.combo.config(state="disabled" if rodando else "readonly")
