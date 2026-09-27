from collections import deque
class AgenteAspiradorMatrizInteligente:
    def __init__(self):
        self.direcao = (0, 1)  # (direcao_v, direcao_h)
        self.posicao_atual = (0, 0)
        self.mapa = {(0, 0): "Desconhecido"}
        self.proximos_passos = []
        self.estados = ["Sujo", "Limpo", "Obstaculo", "Desconhecido"]


    def verificar_estado(self, estado_sujeira, colisao):
        #verificando posição atual do agente
        self.mapa[self.posicao_atual] = estado_sujeira

        #verificando posicoes adjacentes com base na colisao
        posicao_direita = (self.posicao_atual[0], self.posicao_atual[1] + 1)
        if colisao[0][1]:  # Colisão para direita
            self.mapa[posicao_direita] = "Obstaculo"
        elif self.posicao_direita not in self.mapa:
            self.mapa[posicao_direita] = "Desconhecido"

        posicao_baixo = (self.posicao_atual[0] + 1, self.posicao_atual[1])
        if colisao[1][0]:  # Colisão para baixo
            self.mapa[posicao_baixo] = "Obstaculo"
        elif posicao_baixo not in self.mapa:
            self.mapa[posicao_baixo] = "Desconhecido"
        posicao_esquerda = (self.posicao_atual[0], self.posicao_atual[1] - 1)
        if colisao[0][0]:  # Colisão para esquerda
            self.mapa[posicao_esquerda] = "Obstaculo"
        elif posicao_esquerda not in self.mapa:
            self.mapa[posicao_esquerda] = "Desconhecido"
        
        
        posicao_cima = (self.posicao_atual[0] - 1, self.posicao_atual[1])
        if colisao[1][1]:  # Colisão para cima
            self.mapa[posicao_cima] = "Obstaculo"
        elif posicao_cima not in self.mapa:
            self.mapa[posicao_cima] = "Desconhecido"


    

    def executar_plano(self):
        if self.mapa[self.posicao_atual] == "Sujo":
            return "Aspirar"

        if self.proximos_passos:
            proximo_passo = self.proximos_passos.pop(0)
            return proximo_passo
        else:
            return "Nada a fazer"

    def buscar_caminho_bfs(pos_inicial, mapa_mental):
        """
        Realiza uma Busca em Largura (BFS) a partir de pos_inicial (x, y)
        até encontrar a coordenada mais próxima com estado 'DESCONHECIDO' (ou 'SUJO').
        Retorna uma lista de ações: ex: ["Direita", "Baixo", "Esquerda"].
        """
        # Fila guarda: ((x, y), [lista_de_movimentos])
        fila = deque([(pos_inicial, [])])
        
        # Conjunto para não repetições na busca
        visitados = {pos_inicial}

        # Mapeamento de direções relativas e suas ações correspondentes
        movimentos = [
            ((1, 0), "Direita"),
            ((-1, 0), "Esquerda"),
            ((0, 1), "Baixo"),
            ((0, -1), "Cima")
        ]

        while fila:
            (x_atual, y_atual), caminho = fila.popleft()

            # Condição de parada do BFS: Encontrou um objetivo
            estado_celula = mapa_mental.get((x_atual, y_atual))
            if estado_celula == "DESCONHECIDO" or estado_celula == "SUJO":
                return caminho  # Retorna a lista de ações do menor caminho

            # Explora os 4 vizinhos
            for (dx, dy), acao in movimentos:
                nx, ny = x_atual + dx, y_atual + dy
                vizinho = (nx, ny)

                # Verifica se o vizinho existe no mapa mental, se não é obstáculo e não foi visitado
                if vizinho in mapa_mental and vizinho not in visitados:
                    if mapa_mental[vizinho] != "OBSTACULO":
                        visitados.add(vizinho)
                        # Adiciona à fila mantendo o histórico de passos
                        fila.append((vizinho, caminho + [acao]))

        # Se a fila esvaziar e nada for encontrado, o mapa acessível está 100% explorado
        return []


            
 

    def atualizar_posicao(self, acao):
        if acao == "Direita":
            self.posicao_atual = (self.posicao_atual[0], self.posicao_atual[1] + 1)
        elif acao == "Esquerda":
            self.posicao_atual = (self.posicao_atual[0], self.posicao_atual[1] - 1)
        elif acao == "Baixo":
            self.posicao_atual = (self.posicao_atual[0] + 1, self.posicao_atual[1])
        elif acao == "Cima":
            self.posicao_atual = (self.posicao_atual[0] - 1, self.posicao_atual[1])