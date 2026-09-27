from collections import deque

class AgenteAspiradorMatrizInteligente:
    def __init__(self):
        # A posição será baseada em (linha, coluna). Origem (0,0)
        self.posicao_atual = (0, 0)
        self.mapa = {(0, 0): "Desconhecido"}
        self.proximos_passos = []

    def obter_acao(self, estado_sujeira, colisao):
        """Método principal chamado pelo simulador a cada passo."""
        
        # 1. Atualiza o mapa mental com os sensores
        self.verificar_estado(estado_sujeira, colisao)

        # 2. Reação imediata: Se está sujo, aspira
        if estado_sujeira == "Sujo":
            # Assume que vai limpar no simulador, então já anota na memória
            self.mapa[self.posicao_atual] = "Limpo" 
            return "Aspirar"

        # 3. Planejamento: Se não tem passos planejados, busca o próximo destino
        if not self.proximos_passos:
            self.proximos_passos = self.buscar_caminho_bfs(self.posicao_atual, self.mapa)

        # 4. Execução: Se achou um caminho, executa o primeiro passo
        if self.proximos_passos:
            acao = self.proximos_passos.pop(0)
            self.atualizar_posicao(acao)  # O agente atualiza onde ele acha que está
            return acao
        
        # 5. Parada: Se não tem sujeira nem lugar desconhecido acessível
        return "Parar"

    def verificar_estado(self, estado_sujeira, colisao):
        # colisao = [[Cima(0,0), Baixo(0,1)], [Esquerda(1,0), Direita(1,1)]]
        self.mapa[self.posicao_atual] = estado_sujeira

        # Direita (Linha igual, Coluna + 1)
        posicao_direita = (self.posicao_atual[0], self.posicao_atual[1] + 1)
        if colisao[1][1]:  
            self.mapa[posicao_direita] = "Obstaculo"
        elif posicao_direita not in self.mapa:
            self.mapa[posicao_direita] = "Desconhecido"

        # Baixo (Linha + 1, Coluna igual)
        posicao_baixo = (self.posicao_atual[0] + 1, self.posicao_atual[1])
        if colisao[0][1]:  
            self.mapa[posicao_baixo] = "Obstaculo"
        elif posicao_baixo not in self.mapa:
            self.mapa[posicao_baixo] = "Desconhecido"
            
        # Esquerda (Linha igual, Coluna - 1)
        posicao_esquerda = (self.posicao_atual[0], self.posicao_atual[1] - 1)
        if colisao[1][0]:  
            self.mapa[posicao_esquerda] = "Obstaculo"
        elif posicao_esquerda not in self.mapa:
            self.mapa[posicao_esquerda] = "Desconhecido"
        
        # Cima (Linha - 1, Coluna igual)
        posicao_cima = (self.posicao_atual[0] - 1, self.posicao_atual[1])
        if colisao[0][0]:  
            self.mapa[posicao_cima] = "Obstaculo"
        elif posicao_cima not in self.mapa:
            self.mapa[posicao_cima] = "Desconhecido"

    def buscar_caminho_bfs(self, pos_inicial, mapa_mental):
        # Fila guarda: ((linha, coluna), [lista_de_movimentos])
        fila = deque([(pos_inicial, [])])
        visitados = {pos_inicial}

        # Sistema de (Linha, Coluna):
        movimentos = [
            ((0, 1), "Direita"),   # Aumenta coluna
            ((0, -1), "Esquerda"), # Diminui coluna
            ((1, 0), "Baixo"),     # Aumenta linha
            ((-1, 0), "Cima")      # Diminui linha
        ]

        while fila:
            (l_atual, c_atual), caminho = fila.popleft()

            # Condição de parada: Achou desconhecido ou sujo
            estado_celula = mapa_mental.get((l_atual, c_atual))
            if estado_celula == "Desconhecido" or estado_celula == "Sujo":
                return caminho  

            # Explora os 4 vizinhos
            for (dl, dc), acao in movimentos:
                vizinho = (l_atual + dl, c_atual + dc)

                if vizinho in mapa_mental and vizinho not in visitados:
                    if mapa_mental[vizinho] != "Obstaculo":
                        visitados.add(vizinho)
                        fila.append((vizinho, caminho + [acao]))

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