import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from agente_simples import AgenteAspiradorMatriz
from agente_modelo import AgenteAspiradorMatrizInteligente

N_LINHAS = 5
N_COLUNAS = 5

class InterfaceMatrizAspirador:
    def __init__(self, root):
        self.root = root
        self.root.title("Agente Aspirador de Pó - Matriz nxm")
        self.root.geometry("900x650")
        self.root.resizable(False, False)

        self.agentes_disponiveis = {
            "Agente Reativo Simples": AgenteAspiradorMatriz,
            "Agente Baseado em Modelo (Inteligente)": AgenteAspiradorMatrizInteligente
        }

        self.agente = AgenteAspiradorMatriz()

        self.pos_linha = random.randint(0, N_LINHAS - 1)
        self.pos_coluna = random.randint(0, N_COLUNAS - 1)
        self.pos_linha_ini = self.pos_linha
        self.pos_coluna_ini = self.pos_coluna
        
        caminho_base = os.path.dirname(os.path.abspath(__file__))
        caminho_imagem = os.path.join(caminho_base, "aspira_agent.png")

        self.img_agente = None
        try:
            if os.path.exists(caminho_imagem):
                img_original = Image.open(caminho_imagem)
                img_resized = img_original.resize((50, 50), Image.Resampling.LANCZOS)
                self.img_agente = ImageTk.PhotoImage(img_resized)
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")

        self.matriz = [["Limpo" for _ in range(N_COLUNAS)] for _ in range(N_LINHAS)]
        self.particulas_po = {}
        self.obstaculos = set()
        
        self.passos = 0
        self.desempenho_m1 = 0
        self.desempenho_m2 = 0
        self.executando = False

        self.historico_m1 = []
        self.historico_m2 = []

        self._criar_widgets()
        self._gerar_ambiente_aleatorio()
        self._atualizar_interface()

    def _criar_widgets(self):
        # 1. Seleção do Agente
        frame_agente = ttk.LabelFrame(self.root, text=" Seleção do Agente ", padding=10)
        frame_agente.pack(fill="x", padx=15, pady=5)

        ttk.Label(frame_agente, text="Tipo de Agente: ").pack(side="left", padx=5)
        self.combo_agente = ttk.Combobox(
            frame_agente, 
            values=list(self.agentes_disponiveis.keys()),
            state="readonly",
            width=38
        )
        self.combo_agente.current(0)
        self.combo_agente.pack(side="left", padx=5)
        self.combo_agente.bind("<<ComboboxSelected>>", self._trocar_agente)

        # 2. Painel de Controle (Superior)
        frame_top = ttk.LabelFrame(self.root, text=" Painel de Controle ", padding=10)
        frame_top.pack(fill="x", padx=15, pady=5)

        self.btn_step = ttk.Button(frame_top, text="Executar 1 Passo", command=self.passo_simulacao)
        self.btn_step.pack(side="left", padx=5)

        self.btn_auto = ttk.Button(frame_top, text="Iniciar Automático", command=self.toggle_automatico)
        self.btn_auto.pack(side="left", padx=5)

        ttk.Label(frame_top, text=" Passos (T):").pack(side="left", padx=(10, 2))
        self.spin_passos = ttk.Spinbox(frame_top, from_=1, to=500, width=5)
        self.spin_passos.set(25)
        self.spin_passos.pack(side="left", padx=2)

        # Controle de Obstáculos
        ttk.Label(frame_top, text=" Obstáculos:").pack(side="left", padx=(15, 2))
        self.spin_obstaculos = ttk.Spinbox(frame_top, from_=0, to=8, width=4)
        self.spin_obstaculos.set(3)
        self.spin_obstaculos.pack(side="left", padx=2)

        self.btn_reset = ttk.Button(frame_top, text="Nova Configuração (Reset)", command=self.resetar_simulacao)
        self.btn_reset.pack(side="right", padx=5)

        # 3. Conteúdo Central (Grid na Esquerda + Métricas na Direita)
        frame_corpo = ttk.Frame(self.root, padding=10)
        frame_corpo.pack(fill="both", expand=True, padx=15)

        # Canvas (Matriz)
        self.canvas = tk.Canvas(frame_corpo, width=N_COLUNAS * 90, height=N_LINHAS * 90, bg="#ffffff", highlightthickness=1)
        self.canvas.pack(side="left", anchor="n", padx=(0, 20))

        # Painel Lateral de Métricas
        frame_metricas = ttk.LabelFrame(frame_corpo, text=" Métricas e Desempenho ", padding=15)
        frame_metricas.pack(side="left", fill="both", expand=True)

        self.lbl_acao = ttk.Label(frame_metricas, text="Última Ação:\nNenhuma", font=("Arial", 10, "bold"), wraplength=250)
        self.lbl_acao.pack(anchor="w", pady=(0, 10))

        self.lbl_m1 = ttk.Label(frame_metricas, text="Medida 1 (+1 por Aspirar):\n0 pts", font=("Arial", 9))
        self.lbl_m1.pack(anchor="w", pady=5)

        self.lbl_m2 = ttk.Label(frame_metricas, text="Medida 2 (Aspirar +1 / Mover -1):\n0 pts", font=("Arial", 9))
        self.lbl_m2.pack(anchor="w", pady=5)

        ttk.Separator(frame_metricas, orient="horizontal").pack(fill="x", pady=15)

        self.lbl_global = ttk.Label(
            frame_metricas, 
            text="Média Global (Execuções: 0):\n- M1: 0.00 pts\n- M2: 0.00 pts", 
            font=("Arial", 9, "bold"), 
            foreground="#2e6da4",
            justify="left"
        )
        self.lbl_global.pack(anchor="w")

    def _gerar_ambiente_aleatorio(self):
        self.particulas_po.clear()
        self.obstaculos.clear()

        # Sortear número de obstáculos definidos
        try:
            n_obs = int(self.spin_obstaculos.get())
        except ValueError:
            n_obs = 3

        while len(self.obstaculos) < n_obs:
            l = random.randint(0, N_LINHAS - 1)
            c = random.randint(0, N_COLUNAS - 1)
            # Não coloca obstáculo na posição inicial do robô
            if (l, c) != (self.pos_linha, self.pos_coluna):
                self.obstaculos.add((l, c))

        # Sortear Sujeiras
        for l in range(N_LINHAS):
            for c in range(N_COLUNAS):
                if (l, c) in self.obstaculos:
                    self.matriz[l][c] = "Obstaculo"
                    continue

                esta_sujo = random.random() < 0.5
                self.matriz[l][c] = "Sujo" if esta_sujo else "Limpo"
                
                if esta_sujo:
                    particulas = []
                    for _ in range(10):
                        px = random.randint(15, 75)
                        py = random.randint(15, 75)
                        r = random.choice([2, 3])
                        particulas.append((px, py, r))
                    self.particulas_po[(l, c)] = particulas

        self.particulas_ini = self.particulas_po.copy()
        self.matriz_ini = [linha.copy() for linha in self.matriz]

    def _trocar_agente(self, event=None):
        agente_selecionado = self.combo_agente.get()
        classe_agente = self.agentes_disponiveis[agente_selecionado]
        self.agente = classe_agente()
        
        self.historico_m1.clear()
        self.historico_m2.clear()
        self.lbl_global.config(text="Média Global (Execuções: 0):\n- M1: 0.00 pts\n- M2: 0.00 pts")
        self.resetar_simulacao(nova_configuracao=False)

    def _atualizar_interface(self):
        self.canvas.delete("all")
        tamanho = 90

        for l in range(N_LINHAS):
            for c in range(N_COLUNAS):
                x1, y1 = c * tamanho, l * tamanho
                x2, y2 = x1 + tamanho, y1 + tamanho

                if (l, c) in self.obstaculos:
                    # Desenha bloco cinza escuro representando obstáculo
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#555555", outline="#333333", width=2)
                    self.canvas.create_line(x1, y1, x2, y2, fill="#333333", width=2)
                    self.canvas.create_line(x1, y2, x2, y1, fill="#333333", width=2)
                else:
                    cor_fundo = "#fcf8e3" if self.matriz[l][c] == "Sujo" else "#ffffff"
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor_fundo, outline="#dddddd", width=2)

                    if self.matriz[l][c] == "Sujo" and (l, c) in self.particulas_po:
                        for px, py, r in self.particulas_po[(l, c)]:
                            self.canvas.create_oval(x1+px-r, y1+py-r, x1+px+r, y1+py+r, fill="#8a6d3b", outline="#6e5428")

                if l == self.pos_linha and c == self.pos_coluna:
                    if self.img_agente is not None:
                        self.canvas.create_image(x1 + 45, y1 + 45, image=self.img_agente)
                    else:
                        self.canvas.create_oval(x1 + 15, y1 + 15, x2 - 15, y2 - 15, fill="#337ab7")

        self.lbl_m1.config(text=f"Medida 1 (+1 por Aspirar):\n{self.desempenho_m1} pts")
        self.lbl_m2.config(text=f"Medida 2 (Aspirar +1 / Mover -1):\n{self.desempenho_m2} pts (Passos: {self.passos})")

    def _verificar_colisao(self):
        # Verifica paredes ou obstáculos adjacentes
        cima = (self.pos_linha <= 0) or ((self.pos_linha - 1, self.pos_coluna) in self.obstaculos)
        baixo = (self.pos_linha >= N_LINHAS - 1) or ((self.pos_linha + 1, self.pos_coluna) in self.obstaculos)
        esquerda = (self.pos_coluna <= 0) or ((self.pos_linha, self.pos_coluna - 1) in self.obstaculos)
        direita = (self.pos_coluna >= N_COLUNAS - 1) or ((self.pos_linha, self.pos_coluna + 1) in self.obstaculos)

        return [[cima, baixo], [esquerda, direita]]

    def passo_simulacao(self):
        try:
            limite_passos = int(self.spin_passos.get())
        except ValueError:
            limite_passos = 25

        if self.passos >= limite_passos:
            if self.executando: self.toggle_automatico()
            self.lbl_acao.config(text=f"Última Ação:\nLimite de {limite_passos} passos atingido!")
            return

        estado_atual = self.matriz[self.pos_linha][self.pos_coluna]
        colisao = self._verificar_colisao()

        acao = self.agente.obter_acao(estado_atual, colisao)

        if acao == "Parar":
            if self.executando: self.toggle_automatico()
            self.lbl_acao.config(text="Última Ação:\nAgente identificou ambiente limpo!")
            return

        custo_movimento, pontos_aspiracao = 0, 0

        if acao == "Aspirar":
            if self.matriz[self.pos_linha][self.pos_coluna] == "Sujo":
                pontos_aspiracao = 1
                self.matriz[self.pos_linha][self.pos_coluna] = "Limpo"
        elif acao == "Direita" and not colisao[1][1]:
            self.pos_coluna += 1
            custo_movimento = 1
        elif acao == "Esquerda" and not colisao[1][0]:
            self.pos_coluna -= 1
            custo_movimento = 1
        elif acao == "Baixo" and not colisao[0][1]:
            self.pos_linha += 1
            custo_movimento = 1
        elif acao == "Cima" and not colisao[0][0]:
            self.pos_linha -= 1
            custo_movimento = 1

        self.passos += 1
        self.desempenho_m1 += pontos_aspiracao
        self.desempenho_m2 += (pontos_aspiracao - custo_movimento)

        self.lbl_acao.config(text=f"Última Ação:\n{acao} em ({self.pos_linha}, {self.pos_coluna})")
        self._atualizar_interface()

    def toggle_automatico(self):
        if self.executando:
            self.executando = False
            self.btn_auto.config(text="Iniciar Automático")
        else:
            self.executando = True
            self.btn_auto.config(text="Pausar Automático")
            self._loop_automatico()

    def _loop_automatico(self):
        if self.executando:
            self.passo_simulacao()
            self.root.after(300, self._loop_automatico)

    def resetar_simulacao(self, nova_configuracao=True):
        if self.passos > 0:
            self.historico_m1.append(self.desempenho_m1)
            self.historico_m2.append(self.desempenho_m2)

            media_m1 = sum(self.historico_m1) / len(self.historico_m1)
            media_m2 = sum(self.historico_m2) / len(self.historico_m2)

            self.lbl_global.config(
                text=f"Média Global (Execuções: {len(self.historico_m1)}):\n- M1: {media_m1:.2f} pts\n- M2: {media_m2:.2f} pts"
            )

        self.executando = False
        self.btn_auto.config(text="Iniciar Automático")
        
        if nova_configuracao:   
            self.pos_linha = random.randint(0, N_LINHAS - 1)
            self.pos_coluna = random.randint(0, N_COLUNAS - 1)
        else:
            self.pos_linha = self.pos_linha_ini
            self.pos_coluna = self.pos_coluna_ini

        self.passos, self.desempenho_m1, self.desempenho_m2 = 0, 0, 0
        
        agente_selecionado = self.combo_agente.get()
        self.agente = self.agentes_disponiveis[agente_selecionado]()
        
        if nova_configuracao:
            self._gerar_ambiente_aleatorio()
        else:
            self.particulas_po = self.particulas_ini.copy()
            self.matriz = [linha.copy() for linha in self.matriz_ini]

        self.lbl_acao.config(text="Última Ação:\nNenhuma")
        self._atualizar_interface()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceMatrizAspirador(root)
    root.mainloop()