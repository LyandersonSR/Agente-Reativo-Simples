import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from agente_simples import AgenteAspiradorMatriz
from agente_modelo import AgenteAspiradorMatrizInteligente

N_LINHAS = 4
N_COLUNAS = 4

class InterfaceMatrizAspirador:
    def __init__(self, root):
        self.root = root
        self.root.title("Agete Aspirador de Pó - Matriz 4x4")
        self.root.geometry("680x750")
        self.root.resizable(False, False)
        self.colisao = False

        
        self.agentes_disponiveis = {
            "Agente Reativo Simples": AgenteAspiradorMatriz,
            "Agente Baseado em Modelo (Inteligente)": AgenteAspiradorMatrizInteligente
        }

        # Instancia o agente inicial (Reativo Simples por padrão)
        self.agente = AgenteAspiradorMatriz()

        self.pos_linha = 0
        self.pos_coluna = 0

        caminho_base = os.path.dirname(os.path.abspath(__file__))
        caminho_imagem = os.path.join(caminho_base, "aspira_agent.png")

        # Imagem do Robo
        self.img_agente = None
        try:
            if os.path.exists(caminho_imagem):
                img_original = Image.open(caminho_imagem)
                img_resized = img_original.resize((60, 60), Image.Resampling.LANCZOS)
                self.img_agente = ImageTk.PhotoImage(img_resized)
            else:
                print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado.")
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")

        # Matriz 4x4 de estado ('Sujo' ou 'Limpo')
        self.matriz = [["Limpo" for _ in range(N_COLUNAS)] for _ in range(N_LINHAS)]
        
        # Posições fixas do pó para manter consistência visual
        self.particulas_po = {}
        
        # Métricas da simulação atual
        self.passos = 0
        self.desempenho_m1 = 0
        self.desempenho_m2 = 0
        self.executando = False

        # Registro de pontuações globais (Histórico)
        self.historico_m1 = []
        self.historico_m2 = []

        self._gerar_sujeira_aleatoria()
        self._criar_widgets()
        self._atualizar_interface()

    def _gerar_sujeira_aleatoria(self):
        """Preenche o ambiente 4x4 com sujeira aleatória e define padrão do pó."""
        self.particulas_po.clear()
        for l in range(N_LINHAS):
            for c in range(N_COLUNAS):
                esta_sujo = random.random() < 0.5
                self.matriz[l][c] = "Sujo" if esta_sujo else "Limpo"
                
                if esta_sujo:
                    particulas = []
                    for _ in range(12):  # 12 partículas por quadrado
                        px = random.randint(15, 85)
                        py = random.randint(15, 85)
                        r = random.choice([2, 3, 4])
                        particulas.append((px, py, r))
                    self.particulas_po[(l, c)] = particulas

        self.particulas_ini = self.particulas_po.copy()  # Salva o estado inicial para resetar depois
        self.matriz_ini = [linha.copy() for linha in self.matriz]

    def _criar_widgets(self):
        # Painel de Seleção de Agente
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

        # Painel Superior: Controles
        frame_top = ttk.LabelFrame(self.root, text=" Painel de Controle ", padding=10)
        frame_top.pack(fill="x", padx=15, pady=5)

        self.btn_step = ttk.Button(frame_top, text="Executar 1 Passo", command=self.passo_simulacao)
        self.btn_step.pack(side="left", padx=5)

        self.btn_auto = ttk.Button(frame_top, text="Iniciar Automático", command=self.toggle_automatico)
        self.btn_auto.pack(side="left", padx=5)

        self.btn_reset = ttk.Button(frame_top, text="Nova Configuração (Reset)", command=self.resetar_simulacao)
        self.btn_reset.pack(side="left", padx=5)

        # Canvas para Desenhar a Matriz 4x4
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="#ffffff", highlightthickness=1)
        self.canvas.pack(pady=10)

        # Painel do Histórico e Média Global
        frame_info = ttk.LabelFrame(self.root, text=" Métricas e Desempenho ", padding=10)
        frame_info.pack(fill="x", padx=15, pady=5)

        self.lbl_acao = ttk.Label(frame_info, text="Última Ação: Nenhuma", font=("Arial", 10, "bold"))
        self.lbl_acao.pack(anchor="w", pady=2)

        self.lbl_m1 = ttk.Label(frame_info, text="Medida 1 (Atual): 0 pts", font=("Arial", 9))
        self.lbl_m1.pack(anchor="w")

        self.lbl_m2 = ttk.Label(frame_info, text="Medida 2 (Atual - Custo Mov.): 0 pts", font=("Arial", 9))
        self.lbl_m2.pack(anchor="w")

        ttk.Separator(frame_info, orient="horizontal").pack(fill="x", pady=5)

        self.lbl_global = ttk.Label(
            frame_info, 
            text="Pontuação Média Global | Medida 1: 0.00 pts | Medida 2: 0.00 pts (0 execuções)", 
            font=("Arial", 9, "bold"), 
            foreground="#2e6da4"
        )
        self.lbl_global.pack(anchor="w")

    def _trocar_agente(self, event=None):
        """Troca a classe do agente dinamicamente com base na seleção do Combobox."""
        agente_selecionado = self.combo_agente.get()
        classe_agente = self.agentes_disponiveis[agente_selecionado]
        self.agente = classe_agente()
        
        # Reseta o histórico global para comparar métricas do novo agente sem mistura
        self.historico_m1.clear()
        self.historico_m2.clear()
        self.lbl_global.config(
            text="Pontuação Média Global | Medida 1: 0.00 pts | Medida 2: 0.00 pts (0 execuções)"
        )
        
        self.resetar_simulacao(nova_configuracao=False)  # Mantém a sujeira atual, apenas reseta métricas e posição

    def _atualizar_interface(self):
        self.canvas.delete("all")
        tamanho_celula = 100

        for l in range(N_LINHAS):
            for c in range(N_COLUNAS):
                x1 = c * tamanho_celula
                y1 = l * tamanho_celula
                x2 = x1 + tamanho_celula
                y2 = y1 + tamanho_celula

                # Fundo do quadrado
                cor_fundo = "#fcf8e3" if self.matriz[l][c] == "Sujo" else "#ffffff"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor_fundo, outline="#dddddd", width=2)

                # Desenhar o pozinho
                if self.matriz[l][c] == "Sujo" and (l, c) in self.particulas_po:
                    for px, py, r in self.particulas_po[(l, c)]:
                        pos_x = x1 + px
                        pos_y = y1 + py
                        self.canvas.create_oval(
                            pos_x - r, pos_y - r, pos_x + r, pos_y + r, 
                            fill="#8a6d3b", outline="#6e5428"
                        )

                # Desenhar Agente Aspirador
                if l == self.pos_linha and c == self.pos_coluna:
                    if self.img_agente is not None:
                        self.canvas.create_image(x1 + 50, y1 + 50, image=self.img_agente)
                    else:
                        self.canvas.create_oval(x1 + 20, y1 + 20, x2 - 20, y2 - 20, fill="#337ab7", outline="#2e6da4", width=2)
                        self.canvas.create_text(x1 + 50, y1 + 50, text="ASPIRADOR", font=("Arial", 8, "bold"), fill="white")

        # Atualizar textos das métricas
        self.lbl_m1.config(text=f"Medida 1 (1 pt por célula limpa): {self.desempenho_m1} pts")
        self.lbl_m2.config(text=f"Medida 2 (Custo por movimento): {self.desempenho_m2} pts (Passos: {self.passos})")

    def _verificar_colisao(self):
        return [[self.pos_linha <= 0, self.pos_linha >= N_LINHAS - 1],
                [self.pos_coluna <= 0, self.pos_coluna >= N_COLUNAS - 1]]

    def passo_simulacao(self):
        estado_atual = self.matriz[self.pos_linha][self.pos_coluna]

        # 1. Obter ação do agente
        acao = self.agente.obter_acao(estado_atual, self._verificar_colisao())

        # 2. Executar Ação no Ambiente
        custo_movimento = 0
        if acao == "Aspirar":
            self.matriz[self.pos_linha][self.pos_coluna] = "Limpo"
        elif acao == "Direita":
            if self._verificar_colisao()[1][1] is False:
                self.pos_coluna += 1
            custo_movimento = 1
        elif acao == "Esquerda":
            if self._verificar_colisao()[1][0] is False:
                self.pos_coluna -= 1
            custo_movimento = 1
        elif acao == "Baixo":
            if self._verificar_colisao()[0][1] is False:
                self.pos_linha += 1
            custo_movimento = 1

        # 3. Calcular Avaliação de Desempenho
        quadrados_limpos = sum(linha.count("Limpo") for linha in self.matriz)

        self.passos += 1
        self.desempenho_m1 += quadrados_limpos
        self.desempenho_m2 += (quadrados_limpos - custo_movimento)

        # Atualizar Interface
        self.lbl_acao.config(text=f"Última Ação: {acao} em ({self.pos_linha}, {self.pos_coluna})")
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
            self.historico_m1.append(self.desempenho_m1 / self.passos)
            self.historico_m2.append(self.desempenho_m2 / self.passos)

            media_m1 = sum(self.historico_m1) / len(self.historico_m1)
            media_m2 = sum(self.historico_m2) / len(self.historico_m2)

            self.lbl_global.config(
                text=f"Pontuação Média Global por Passo | Medida 1: {media_m1:.2f} pts | Medida 2: {media_m2:.2f} pts ({len(self.historico_m1)} execuções)"
            )

        self.executando = False
        self.btn_auto.config(text="Iniciar Automático")
        self.pos_linha = 0
        self.pos_coluna = 0
        self.passos = 0
        self.desempenho_m1 = 0
        self.desempenho_m2 = 0
        
        # Reiniciar o estado interno do agente selecionado
        agente_selecionado = self.combo_agente.get()
        classe_agente = self.agentes_disponiveis[agente_selecionado]
        self.agente = classe_agente()
        if nova_configuracao:
            self._gerar_sujeira_aleatoria()
        else:
            self.particulas_po = self.particulas_ini.copy()  # Mantém a sujeira inicial
            self.matriz = [linha.copy() for linha in self.matriz_ini]
        self.lbl_acao.config(text="Última Ação: Nenhuma")
        self._atualizar_interface()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceMatrizAspirador(root)
    root.mainloop()