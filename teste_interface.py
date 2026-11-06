"""teste_interface.py - Simula o uso da interface (rodar com: xvfb-run -a python3 teste_interface.py)"""
import time
from interface import App
from algoritmos import eh_caminho_valido

def esperar(app, limite=60):
    t0 = time.time()
    while app.rodando and time.time() - t0 < limite:
        app.update(); time.sleep(0.005)
    assert not app.rodando, "animação não terminou"

def capturar(app, nome):
    """Captura da janela (opcional: precisa do Pillow; se faltar, apenas ignora)."""
    try:
        import os, tempfile
        from PIL import ImageGrab
        app.update_idletasks(); app.update()
        x, y = app.winfo_rootx(), app.winfo_rooty()
        destino = os.path.join(tempfile.gettempdir(), nome)
        ImageGrab.grab(bbox=(x, y, x + app.winfo_width(), y + app.winfo_height())).save(destino)
    except Exception as erro:
        print("(captura de tela ignorada:", type(erro).__name__ + ")")

app = App(); app.update()
app.vel.set(10)

# 1) Fluxo completo nos 3 tamanhos: BFS, depois DFS no MESMO labirinto
for tam in ("Pequeno", "Médio", "Grande"):
    app.var_tamanho.set(tam); app.novo_labirinto(); app.update()
    assert app.resultados == {}
    app.executar("BFS"); esperar(app)
    app.executar("DFS"); esperar(app)
    b, d = app.resultados["BFS"], app.resultados["DFS"]
    assert eh_caminho_valido(app.grafo, b.caminho) and eh_caminho_valido(app.grafo, d.caminho)
    assert app.var[("BFS", "visitados")].get() == str(b.num_visitados)
    assert app.var[("DFS", "comprimento")].get() == str(d.comprimento)
    assert b.comprimento <= d.comprimento
    assert str(app.btn_bfs["state"]) == "normal"
    print(f"{tam:8} OK | BFS {b.num_visitados}/{b.comprimento} | DFS {d.num_visitados}/{d.comprimento}")
    print("         Comparação:", app.var_comp.get().replace("\n", " | "))
    if tam == "Médio":
        capturar(app, "tela_medio.png")

# 2) Entrada e saída mantêm a cor após a animação
assert app.canvas.itemcget(app.ids[app.entrada], "fill") == "#16a34a"
assert app.canvas.itemcget(app.ids[app.saida], "fill") == "#dc2626"
# o caminho do último algoritmo está pintado de dourado
meio = app.resultados["DFS"].caminho[len(app.resultados["DFS"].caminho)//2]
assert app.canvas.itemcget(app.ids[meio], "fill") == "#f5b400"
print("OK: cores de entrada/saída e caminho")

# 3) Limpar no meio da animação (velocidade lenta) cancela tudo e libera os botões
app.vel.set(1); app.executar("BFS")
for _ in range(20): app.update(); time.sleep(0.01)
assert app.rodando
assert str(app.btn_bfs["state"]) == "disabled" and str(app.btn_novo["state"]) == "disabled"
assert str(app.combo["state"]) == "disabled"
app.limpar(); app.update()
assert not app.rodando and app.resultados == {} and app._job is None
assert app.var[("BFS", "visitados")].get() == "—"
assert str(app.btn_bfs["state"]) == "normal"
assert all(app.canvas.itemcget(app.ids[v], "fill") in ("#ffffff", "#16a34a", "#dc2626") for v in app.ids)
print("OK: Limpar cancela a animação e reinicia")

# 4) Novo labirinto no meio de uma execução não deixa 'fantasmas'
app.vel.set(1); app.executar("DFS")
for _ in range(10): app.update(); time.sleep(0.01)
app.novo_labirinto(); 
for _ in range(30): app.update(); time.sleep(0.01)
assert not app.rodando and app.resultados == {}
print("OK: Novo labirinto durante a animação")
capturar(app, "tela_novo.png")
app.destroy()
print("\nTodos os testes da interface passaram.")
