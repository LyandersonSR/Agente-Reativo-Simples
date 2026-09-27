import random
import matplotlib.pyplot as plt
from agente_simples import AgenteAspiradorMatriz
from agente_modelo import AgenteAspiradorMatrizInteligente
import numpy as np

N_LINHAS = 5
N_COLUNAS = 5
N_AMBIENTES = 1000  # Quantidade de ambientes gerados por passo

def gerar_ambiente_inicial():
    """Gera uma matriz 4x4 com 50% de chance de sujeira em cada célula."""
    matriz = [["Limpo" for _ in range(N_COLUNAS)] for _ in range(N_LINHAS)]
    for l in range(N_LINHAS):
        for c in range(N_COLUNAS):
            if random.random() < 0.5:
                matriz[l][c] = "Sujo"
    return matriz

def verificar_colisao(pos_linha, pos_coluna):
    """Verifica os limites da matriz (paredes)."""
    return [[pos_linha <= 0, pos_linha >= N_LINHAS - 1],
            [pos_coluna <= 0, pos_coluna >= N_COLUNAS - 1]]

def simular_agente(classe_agente, matriz_inicial, max_passos, pos_linha_ini, pos_coluna_ini):
    """Roda a simulação para um agente específico a partir de uma posição inicial."""
    matriz = [linha.copy() for linha in matriz_inicial]
    agente = classe_agente()
    
    # Inicia na posição aleatória fornecida
    pos_linha = pos_linha_ini
    pos_coluna = pos_coluna_ini
    
    desempenho_m1 = 0
    desempenho_m2 = 0

    for _ in range(max_passos):
        estado_atual = matriz[pos_linha][pos_coluna]
        colisao = verificar_colisao(pos_linha, pos_coluna)
        
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
            if not colisao[1][1]:
                pos_coluna += 1
            custo_movimento = 1
        elif acao == "Esquerda":
            if not colisao[1][0]:
                pos_coluna -= 1
            custo_movimento = 1
        elif acao == "Baixo":
            if not colisao[0][1]:
                pos_linha += 1
            custo_movimento = 1
        elif acao == "Cima":
            if not colisao[0][0]:
                pos_linha -= 1
            custo_movimento = 1

        desempenho_m1 += pontos_aspiracao
        desempenho_m2 += (pontos_aspiracao - custo_movimento)

    return desempenho_m1, desempenho_m2

def executar_experimento():
    intervalo_passos = list(range(25, 100,5))
    
    # Histórico de resultados
    resultados_simples_m1, resultados_simples_m2 = [], []
    resultados_modelo_m1, resultados_modelo_m2 = [], []

    print(f"Executando simulações (Média de {N_AMBIENTES} ambientes por passo)...")

    for passos in intervalo_passos:
        media_simples_m1, media_simples_m2 = 0, 0
        media_modelo_m1, media_modelo_m2 = 0, 0
        
        for _ in range(N_AMBIENTES):
            matriz_inicial = gerar_ambiente_inicial()
            
            # Sorteia uma posição inicial aleatória para o ambiente atual
            pos_ini_linha = random.randint(0, N_LINHAS - 1)
            pos_ini_coluna = random.randint(0, N_COLUNAS - 1)
            
            # Avalia o Agente Simples
            m1, m2 = simular_agente(AgenteAspiradorMatriz, matriz_inicial, passos, pos_ini_linha, pos_ini_coluna)
            media_simples_m1 += m1
            media_simples_m2 += m2
            
            # Avalia o Agente Baseado em Modelo
            m1, m2 = simular_agente(AgenteAspiradorMatrizInteligente, matriz_inicial, passos, pos_ini_linha, pos_ini_coluna)
            media_modelo_m1 += m1
            media_modelo_m2 += m2
            
        # Calcula e armazena a média dos ambientes
        resultados_simples_m1.append(media_simples_m1 / (N_AMBIENTES*np.sqrt(N_LINHAS*N_COLUNAS)))
        resultados_simples_m2.append(media_simples_m2 / (N_AMBIENTES*np.sqrt(N_LINHAS*N_COLUNAS)))
        
        resultados_modelo_m1.append(media_modelo_m1 / (N_AMBIENTES*np.sqrt(N_LINHAS*N_COLUNAS)))
        resultados_modelo_m2.append(media_modelo_m2 / (N_AMBIENTES*np.sqrt(N_LINHAS*N_COLUNAS)))

    # Plotagem
    plt.figure(figsize=(12, 6))

    # Gráfico da Medida 1
    plt.subplot(1, 2, 1)
    plt.plot(intervalo_passos, resultados_simples_m1, label='Reativo Simples', marker='o')
    plt.plot(intervalo_passos, resultados_modelo_m1, label='Baseado em Modelo', marker='s')
    plt.title('Medida 1: Eficiência de Limpeza (+1 por sujeira)')
    plt.xlabel('Número de Passos (T)')
    plt.ylabel(f'Pontuação Média ({N_AMBIENTES} amb.)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # Gráfico da Medida 2
    plt.subplot(1, 2, 2)
    plt.plot(intervalo_passos, resultados_simples_m2, label='Reativo Simples', marker='o')
    plt.plot(intervalo_passos, resultados_modelo_m2, label='Baseado em Modelo', marker='s')
    plt.title('Medida 2: Eficiência Energética (+1 aspirar, -1 mover)')
    plt.xlabel('Número de Passos (T)')
    plt.ylabel(f'Pontuação Média ({N_AMBIENTES} amb.)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    executar_experimento()