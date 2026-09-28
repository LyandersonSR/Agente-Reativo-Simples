import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from agente_simples import AgenteAspiradorMatriz
from agente_modelo import AgenteAspiradorMatrizInteligente

N_LINHAS = 5
N_COLUNAS = 5
N_AMBIENTES = 1000
N_OBSTACULOS = 3

# =====================================================================
# LÓGICA DA SIMULAÇÃO (Encontrar extremos e coletar dados para gráficos)
# =====================================================================

def gerar_ambiente_inicial():
    # Sorteia a posição inicial do agente primeiro
    pos_linha = random.randint(0, N_LINHAS - 1)
    pos_coluna = random.randint(0, N_COLUNAS - 1)
    
    obstaculos = set()
    # Garante que criaremos a quantidade certa de obstáculos, e não sobre o agente
    while len(obstaculos) < N_OBSTACULOS:
        l = random.randint(0, N_LINHAS - 1)
        c = random.randint(0, N_COLUNAS - 1)
        if (l, c) != (pos_linha, pos_coluna):
            obstaculos.add((l, c))
            
    matriz = [["Limpo" for _ in range(N_COLUNAS)] for _ in range(N_LINHAS)]
    
    for l in range(N_LINHAS):
        for c in range(N_COLUNAS):
            if (l, c) in obstaculos:
                matriz[l][c] = "Obstaculo"
            else:
                if random.random() < 0.5:
                    matriz[l][c] = "Sujo"
                    
    return matriz, pos_linha, pos_coluna

def verificar_colisao(pos_linha, pos_coluna, matriz):
    cima = (pos_linha <= 0) or (matriz[pos_linha - 1][pos_coluna] == "Obstaculo")
    baixo = (pos_linha >= N_LINHAS - 1) or (matriz[pos_linha + 1][pos_coluna] == "Obstaculo")
    esquerda = (pos_coluna <= 0) or (matriz[pos_linha][pos_coluna - 1] == "Obstaculo")
    direita = (pos_coluna >= N_COLUNAS - 1) or (matriz[pos_linha][pos_coluna + 1] == "Obstaculo")
    return [[cima, baixo], [esquerda, direita]]

def simular_agente(classe_agente, matriz_inicial, max_passos, pos_linha_ini, pos_coluna_ini):
    matriz = [linha.copy() for linha in matriz_inicial]
    agente = classe_agente()
    pos_linha, pos_coluna = pos_linha_ini, pos_coluna_ini
    
    pontuacao_m1 = 0 # Medida 1: Apenas sujeira aspirada
    pontuacao_m2 = 0 # Medida 2: Sujeira aspirada - custo de movimento

    for _ in range(max_passos):
        estado_atual = matriz[pos_linha][pos_coluna]
        colisao = verificar_colisao(pos_linha, pos_coluna, matriz)
        acao = agente.obter_acao(estado_atual, colisao)
        
        if acao == "Parar":
            break

        custo_movimento = 0
        pontos_aspiracao = 0

        if acao == "Aspirar":
            if matriz[pos_linha][pos_coluna] == "Sujo":
                pontos_aspiracao = 1
                matriz[pos_linha][pos_coluna] = "Limpo"
        elif acao == "Direita":
            if not colisao[1][1]: pos_coluna += 1
            custo_movimento = 1
        elif acao == "Esquerda":
            if not colisao[1][0]: pos_coluna -= 1
            custo_movimento = 1
        elif acao == "Baixo":
            if not colisao[0][1]: pos_linha += 1
            custo_movimento = 1
        elif acao == "Cima":
            if not colisao[0][0]: pos_linha -= 1
            custo_movimento = 1

        pontuacao_m1 += pontos_aspiracao
        pontuacao_m2 += (pontos_aspiracao - custo_movimento)

    return pontuacao_m1, pontuacao_m2

def executar_e_coletar_extremos():
    extremos = {
        "Simples": {
            "melhor": {"score": -float('inf'), "matriz": None, "pos": None, "passos": None},
            "pior": {"score": float('inf'), "matriz": None, "pos": None, "passos": None}
        },
        "Modelo": {
            "melhor": {"score": -float('inf'), "matriz": None, "pos": None, "passos": None},
            "pior": {"score": float('inf'), "matriz": None, "pos": None, "passos": None}
        }
    }

    historico_passos = {
        "passos": [],
        "media_simples_m1": [],
        "media_modelo_m1": [],
        "media_simples_m2": [],
        "media_modelo_m2": []
    }

    max_sujeiras = (N_LINHAS * N_COLUNAS) - N_OBSTACULOS
    tracker_sujeira = {
        "simples_m1": {i: [] for i in range(max_sujeiras + 1)},
        "modelo_m1": {i: [] for i in range(max_sujeiras + 1)},
        "simples_m2": {i: [] for i in range(max_sujeiras + 1)},
        "modelo_m2": {i: [] for i in range(max_sujeiras + 1)}
    }

    intervalo_passos = range(25, 61)
    print("Processando simulações com obstáculos para encontrar os extremos e gerar gráficos...")

    for passos in intervalo_passos:
        soma_simp_m1, soma_simp_m2 = 0, 0
        soma_mod_m1, soma_mod_m2 = 0, 0

        for _ in range(N_AMBIENTES):
            matriz_inicial, pos_ini_linha, pos_ini_coluna = gerar_ambiente_inicial()
            qtd_sujeira = sum(linha.count("Sujo") for linha in matriz_inicial)
            pos_inicial = (pos_ini_linha, pos_ini_coluna)
            
            # Simples
            m1_simp, m2_simp = simular_agente(AgenteAspiradorMatriz, matriz_inicial, passos, pos_ini_linha, pos_ini_coluna)
            soma_simp_m1 += m1_simp
            soma_simp_m2 += m2_simp
            tracker_sujeira["simples_m1"][qtd_sujeira].append(m1_simp)
            tracker_sujeira["simples_m2"][qtd_sujeira].append(m2_simp)

            # Critério de extremo (M2)
            if m2_simp > extremos["Simples"]["melhor"]["score"]:
                extremos["Simples"]["melhor"] = {"score": m2_simp, "matriz": [l.copy() for l in matriz_inicial], "pos": pos_inicial, "passos": passos}
            if m2_simp < extremos["Simples"]["pior"]["score"]:
                extremos["Simples"]["pior"] = {"score": m2_simp, "matriz": [l.copy() for l in matriz_inicial], "pos": pos_inicial, "passos": passos}
            
            # Modelo
            m1_mod, m2_mod = simular_agente(AgenteAspiradorMatrizInteligente, matriz_inicial, passos, pos_ini_linha, pos_ini_coluna)
            soma_mod_m1 += m1_mod
            soma_mod_m2 += m2_mod
            tracker_sujeira["modelo_m1"][qtd_sujeira].append(m1_mod)
            tracker_sujeira["modelo_m2"][qtd_sujeira].append(m2_mod)

            if m2_mod > extremos["Modelo"]["melhor"]["score"]:
                extremos["Modelo"]["melhor"] = {"score": m2_mod, "matriz": [l.copy() for l in matriz_inicial], "pos": pos_inicial, "passos": passos}
            if m2_mod < extremos["Modelo"]["pior"]["score"]:
                extremos["Modelo"]["pior"] = {"score": m2_mod, "matriz": [l.copy() for l in matriz_inicial], "pos": pos_inicial, "passos": passos}
        
        # Histórico por passos
        historico_passos["passos"].append(passos)
        historico_passos["media_simples_m1"].append(soma_simp_m1 / N_AMBIENTES)
        historico_passos["media_modelo_m1"].append(soma_mod_m1 / N_AMBIENTES)
        historico_passos["media_simples_m2"].append(soma_simp_m2 / N_AMBIENTES)
        historico_passos["media_modelo_m2"].append(soma_mod_m2 / N_AMBIENTES)

    # Consolidar médias por quantidade de sujeira
    historico_sujeira = {"qtd": [], "simples_m1": [], "modelo_m1": [], "simples_m2": [], "modelo_m2": []}
    for i in range(max_sujeiras + 1):
        if len(tracker_sujeira["simples_m1"][i]) > 0:
            historico_sujeira["qtd"].append(i)
            historico_sujeira["simples_m1"].append(sum(tracker_sujeira["simples_m1"][i]) / len(tracker_sujeira["simples_m1"][i]))
            historico_sujeira["modelo_m1"].append(sum(tracker_sujeira["modelo_m1"][i]) / len(tracker_sujeira["modelo_m1"][i]))
            historico_sujeira["simples_m2"].append(sum(tracker_sujeira["simples_m2"][i]) / len(tracker_sujeira["simples_m2"][i]))
            historico_sujeira["modelo_m2"].append(sum(tracker_sujeira["modelo_m2"][i]) / len(tracker_sujeira["modelo_m2"][i]))

    return extremos, historico_passos, historico_sujeira

# =====================================================================
# INTERFACE GRÁFICA TKINTER
# =====================================================================

class VisualizadorExtremosTk:
    def __init__(self, root, extremos, historico_passos, historico_sujeira):
        self.root = root
        self.root.title("Simulação Aspirador de Pó - Ambientes e Desempenho (Com Obstáculos)")
        self.root.geometry("1000x750")
        self.root.resizable(False, False)
        
        self.extremos = extremos
        self.historico_passos = historico_passos
        self.historico_sujeira = historico_sujeira
        
        caminho_base = os.path.dirname(os.path.abspath(__file__))
        caminho_imagem = os.path.join(caminho_base, "aspira_agent.png")
        self.img_agente = None
        
        try:
            if os.path.exists(caminho_imagem):
                img_original = Image.open(caminho_imagem)
                img_resized = img_original.resize((60, 60), Image.Resampling.LANCZOS)
                self.img_agente = ImageTk.PhotoImage(img_resized)
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")

        self._criar_interface()

    def _criar_interface(self):
        ttk.Label(self.root, text="Resultados da Simulação (1000 Ambientes/Passo)", font=("Arial", 14, "bold")).pack(pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=20, pady=10)

        # Abas de Gráficos de Passos (M1 e M2)
        self._criar_aba_grafico_passos("Gráfico (Passos) - M1", 
                                       self.historico_passos["media_simples_m1"], 
                                       self.historico_passos["media_modelo_m1"], 
                                       "Pontuação (Sujeira Aspirada)", 
                                       "Desempenho M1 vs Passos")
                                
        self._criar_aba_grafico_passos("Gráfico (Passos) - M2", 
                                       self.historico_passos["media_simples_m2"], 
                                       self.historico_passos["media_modelo_m2"], 
                                       "Pontuação (Limpeza - Movimentos)", 
                                       "Desempenho M2 vs Passos")

        # Nova Aba: Gráficos de Sujeira (M1 e M2 juntos)
        self._criar_aba_grafico_sujeira("Gráficos vs Quantidade de Sujeira")

        # Abas de Matrizes Extremas
        self._criar_aba_matriz("Simples - Melhor (M2)", self.extremos["Simples"]["melhor"])
        self._criar_aba_matriz("Simples - Pior (M2)", self.extremos["Simples"]["pior"])
        self._criar_aba_matriz("Modelo - Melhor (M2)", self.extremos["Modelo"]["melhor"])
        self._criar_aba_matriz("Modelo - Pior (M2)", self.extremos["Modelo"]["pior"])

    def _criar_aba_grafico_passos(self, titulo_aba, dados_simples, dados_modelo, label_y, titulo_grafico):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=titulo_aba)

        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        ax.plot(self.historico_passos["passos"], dados_simples, label="Agente Reativo Simples", color="red", linestyle="--", marker="o")
        ax.plot(self.historico_passos["passos"], dados_modelo, label="Agente Baseado em Modelo", color="green", marker="s")
        
        ax.set_title(titulo_grafico)
        ax.set_xlabel("Máximo de Passos (T)")
        ax.set_ylabel(label_y)
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.7)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

    def _criar_aba_grafico_sujeira(self, titulo_aba):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=titulo_aba)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100)
        
        # Gráfico M1 vs Sujeira
        ax1.plot(self.historico_sujeira["qtd"], self.historico_sujeira["simples_m1"], label="Simples", color="red", linestyle="--", marker="o")
        ax1.plot(self.historico_sujeira["qtd"], self.historico_sujeira["modelo_m1"], label="Modelo", color="green", marker="s")
        ax1.set_title("Medida 1 Média vs Qtd. Sujeira Inicial")
        ax1.set_xlabel("Quantidade de Sujeira")
        ax1.set_ylabel("Pontuação Média (M1)")
        ax1.legend()
        ax1.grid(True, linestyle=":", alpha=0.7)

        # Gráfico M2 vs Sujeira
        ax2.plot(self.historico_sujeira["qtd"], self.historico_sujeira["simples_m2"], label="Simples", color="red", linestyle="--", marker="o")
        ax2.plot(self.historico_sujeira["qtd"], self.historico_sujeira["modelo_m2"], label="Modelo", color="green", marker="s")
        ax2.set_title("Medida 2 Média vs Qtd. Sujeira Inicial")
        ax2.set_xlabel("Quantidade de Sujeira")
        ax2.set_ylabel("Pontuação Média (M2)")
        ax2.legend()
        ax2.grid(True, linestyle=":", alpha=0.7)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

    def _criar_aba_matriz(self, titulo, dados):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=titulo)

        info_texto = f"Pontuação (Medida 2): {dados['score']} pts  |  Passos Limite (T): {dados['passos']}"
        ttk.Label(frame, text=info_texto, font=("Arial", 11, "bold"), foreground="#2e6da4").pack(pady=10)

        canvas = tk.Canvas(frame, width=N_COLUNAS*100, height=N_LINHAS*100, bg="#ffffff", highlightthickness=1)
        canvas.pack(pady=5)

        self._desenhar_matriz(canvas, dados["matriz"], dados["pos"])

    def _desenhar_matriz(self, canvas, matriz, pos_inicial):
        tamanho_celula = 100
        pos_linha, pos_coluna = pos_inicial

        for l in range(N_LINHAS):
            for c in range(N_COLUNAS):
                x1 = c * tamanho_celula
                y1 = l * tamanho_celula
                x2 = x1 + tamanho_celula
                y2 = y1 + tamanho_celula

                if matriz[l][c] == "Obstaculo":
                    # Desenha Obstáculo
                    canvas.create_rectangle(x1, y1, x2, y2, fill="#555555", outline="#333333", width=2)
                    canvas.create_line(x1, y1, x2, y2, fill="#333333", width=2)
                    canvas.create_line(x1, y2, x2, y1, fill="#333333", width=2)
                else:
                    # Fundo normal
                    cor_fundo = "#fcf8e3" if matriz[l][c] == "Sujo" else "#ffffff"
                    canvas.create_rectangle(x1, y1, x2, y2, fill=cor_fundo, outline="#dddddd", width=2)

                    if matriz[l][c] == "Sujo":
                        for _ in range(12):
                            px, py = random.randint(15, 85), random.randint(15, 85)
                            r = random.choice([2, 3, 4])
                            canvas.create_oval(x1+px-r, y1+py-r, x1+px+r, y1+py+r, fill="#8a6d3b", outline="#6e5428")

                if l == pos_linha and c == pos_coluna:
                    if self.img_agente:
                        canvas.create_image(x1 + 50, y1 + 50, image=self.img_agente)
                    else:
                        canvas.create_oval(x1 + 20, y1 + 20, x2 - 20, y2 - 20, fill="#337ab7", outline="#2e6da4", width=2)
                        canvas.create_text(x1 + 50, y1 + 50, text="INÍCIO", font=("Arial", 8, "bold"), fill="white")

if __name__ == "__main__":
    dados_extremos, dados_passos, dados_sujeira = executar_e_coletar_extremos()
    root = tk.Tk()
    app = VisualizadorExtremosTk(root, dados_extremos, dados_passos, dados_sujeira)
    root.mainloop()