# agente_modelo.py

class AgenteAspiradorMatrizInteligente:
    def __init__(self):
        self.direcao = (0, 1)  # (direcao_v, direcao_h)
        self.posicao_atual = (0, 0)
        self.mapa = {(0, 0): "Desconhecido"}
        self.estados = ["Sujo", "Limpo", "Obstaculo", "Desconhecido"]

    def obter_acao(self, estado_sujeira, colisao):
        if estado_sujeira == "Sujo":
            self.mapa[self.posicao_atual] = "Limpo"
            return "Aspirar"

        # Lógica de varredura inteligente
        if self.direcao == (0, 1):  # direita
            if (not colisao[0][1]) and (colisao[1][1]):  # Colisão para direita
                self.direcao = (0, -1)  # Muda para esquerda
                return "Baixo"
            elif (colisao[0][1]) and (colisao[1][1]):  # Colisão para baixo
                self.direcao = (0, -1)  # Muda para esquerda
                return "Esquerda"
            else:
                return "Direita"

        if self.direcao == (0, -1):  # esquerda
            if (not colisao[0][1]) and (colisao[1][0]):  # Colisão para esquerda
                self.direcao = (0, 1)  # Muda para direita
                return "Baixo"
            elif colisao[0][1] and colisao[1][0]:  # Colisão para baixo
                self.direcao = (0, 1)  # Muda para direita
                return "Direita"
            else:
                return "Esquerda"