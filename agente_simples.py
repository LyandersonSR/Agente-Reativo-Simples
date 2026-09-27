class AgenteAspiradorMatriz:
    def __init__(self):
        # (linha, coluna) -> direcao_h: 1 para direita, -1 para esquerda
        self.direcao = (0, 1) 
        self.modo = 0  # 0: descendo na matriz, 1: subindo na matriz

    def obter_acao(self, estado_sujeira, colisao):
        # Mapeamento da estrutura de colisao:
        # colisao[0][0] = Cima | colisao[0][1] = Baixo
        # colisao[1][0] = Esquerda | colisao[1][1] = Direita

        if estado_sujeira == "Sujo":
            return "Aspirar"

        # 1. Se estiver indo para a DIREITA
        if self.direcao == (0, 1):
            if colisao[1][1]:  # Bloqueado à DIREITA
                self.direcao = (0, -1)  # Inverte para Esquerda
                
                # Tenta descer se não houver colisão abaixo
                if not colisao[0][1] and self.modo == 0:
                    return "Baixo"
                # Tenta subir se não houver colisão acima
                elif not colisao[0][0] and self.modo == 1:
                    return "Cima"
                # Se não der pra descer/subir no modo atual, tenta o outro lado
                elif not colisao[0][1]:
                    self.modo = 0
                    return "Baixo"
                elif not colisao[0][0]:
                    self.modo = 1
                    return "Cima"
                else:
                    return "Esquerda"  # Se tudo estiver bloqueado, apenas recua
            else:
                return "Direita"

        # 2. Se estiver indo para a ESQUERDA
        if self.direcao == (0, -1):
            if colisao[1][0]:  # Bloqueado à ESQUERDA
                self.direcao = (0, 1)  # Inverte para Direita
                
                # Tenta descer se não houver colisão abaixo
                if not colisao[0][1] and self.modo == 0:
                    return "Baixo"
                # Tenta subir se não houver colisão acima
                elif not colisao[0][0] and self.modo == 1:
                    return "Cima"
                # Se não der pra descer/subir no modo atual, tenta o outro lado
                elif not colisao[0][1]:
                    self.modo = 0
                    return "Baixo"
                elif not colisao[0][0]:
                    self.modo = 1
                    return "Cima"
                else:
                    return "Direita"  # Se tudo estiver bloqueado, apenas recua
            else:
                return "Esquerda"