class AgenteAspiradorMatriz:
    def __init__(self):
        # Direção horizontal de varredura: (direcao_v, direcao_h)
        self.direcao = (0, 1)
        self.modo = 0

    def obter_acao(self, estado_sujeira, colisao):
        """
        Regra Condição-Ação Reativa com padrão de varredura em matriz:
        1. Se o quadrado atual está sujo -> Aspirar
        2. Se está limpo -> Move-se no padrão zig-zag para cobrir a matriz
        """
        if estado_sujeira == "Sujo":
            return "Aspirar"

        if self.direcao == (0, 1):  # direita
            if (not colisao[0][1]) and (not colisao[0][0]) and(colisao[1][1]):  # Colisão para direita
                self.direcao = (0, -1)  # Muda para esquerda
                return "Baixo" if self.modo == 0 else "Cima"
            elif (colisao[0][1]) and (colisao[1][1]):  # Colisão para baixo
                self.direcao = (0, -1)  # Muda para esquerda
                return "Esquerda"
            elif (colisao[0][0]) and (colisao[1][1]):  # Colisão para cima
                self.direcao = (0, -1)  # Muda para esquerda
                self.modo = 0
                return "Baixo"
            else:
                return "Direita"

        if self.direcao == (0, -1):  # esquerda
            if (not colisao[0][1]) and (not colisao[0][0]) and (colisao[1][0]):  # Colisão para esquerda
                self.direcao = (0, 1)  # Muda para direita
                return "Baixo" if self.modo == 0 else "Cima"
            elif colisao[0][1] and colisao[1][0]:  # Colisão para baixo
                self.direcao = (0, 1)  # Muda para direita
                self.modo = 1
                return "Cima"
            elif colisao[0][0] and colisao[1][0]:  # Colisão para cima
                self.direcao = (0, 1)  # Muda para direita
                return "Direita"
            else:
                return "Esquerda"