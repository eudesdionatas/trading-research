import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.performance.backtester import rodar_backtest

# Configuração de caminhos globais
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
STRATEGIES_DIR = os.path.join(BASE_DIR, "data", "strategies")


def listar_estrategias_processadas():
    """Lê a pasta strategies e retorna os ativos e estratégias disponíveis."""
    # Proteção caso a pasta não exista
    if not os.path.exists(STRATEGIES_DIR):
        return []
        
    arquivos = [f for f in os.listdir(STRATEGIES_DIR) if f.endswith(".csv")]
    
    opcoes = []
    for arq in arquivos:
        partes = arq.replace(".csv", "").split("_", 2)
        if len(partes) >= 3:
            ativo, tempo, estrategia = partes[0], partes[1], partes[2]
            opcoes.append((ativo, tempo, estrategia))
            
    return opcoes


def plotar_desempenho(df_trades, ativo, tempo, nome_estrategia, capital_inicial):
    """Gera o gráfico da Curva de Capital (R$) e Drawdown Máximo (%)."""
    print("\nGerando gráfico de performance...")
    
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("Curva de Capital Reinvestido (R$)", "Drawdown (Queda do Topo Histórico %)"),
        row_heights=[0.7, 0.3]
    )

    # 1. Gráfico Superior: Curva de Capital em Reais
    fig.add_trace(go.Scatter(
        x=df_trades["Data_Saida"], 
        y=df_trades["Capital_Acumulado"],
        mode='lines', 
        name='Saldo (R$)', 
        line=dict(color='limegreen', width=2),
        fill='tozeroy', 
        fillcolor='rgba(50, 205, 50, 0.1)'
    ), row=1, col=1)

    # Marcar os pontos de Gain e Loss na curva
    gains = df_trades[df_trades["Resultado_R$"] > 0]
    losses = df_trades[df_trades["Resultado_R$"] <= 0]
    
    fig.add_trace(go.Scatter(
        x=gains["Data_Saida"], y=gains["Capital_Acumulado"],
        mode='markers', name='Trade Win', marker=dict(color='lime', size=6, symbol='triangle-up')
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=losses["Data_Saida"], y=losses["Capital_Acumulado"],
        mode='markers', name='Trade Loss', marker=dict(color='red', size=6, symbol='triangle-down')
    ), row=1, col=1)

    # Adiciona uma linha horizontal pontilhada mostrando o Zero-a-Zero (Capital Inicial)
    fig.add_hline(y=capital_inicial, line_dash="dot", row=1, col=1, line_color="gray", annotation_text="Breakeven")

    # 2. Gráfico Inferior: Mancha de Drawdown em Porcentagem
    fig.add_trace(go.Scatter(
        x=df_trades["Data_Saida"], 
        y=df_trades["Drawdown_%"],
        mode='lines', 
        name='Drawdown (%)', 
        line=dict(color='crimson', width=1),
        fill='tozeroy', 
        fillcolor='rgba(220, 20, 60, 0.3)'
    ), row=2, col=1)

    # Configuração do Layout
    fig.update_layout(
        title=f"Evolução de Caixa: {ativo} ({tempo}) - {nome_estrategia}",
        template="plotly_dark",
        height=800,
        hovermode="x unified",
        showlegend=True
    )
    
    # Exibir no navegador
    fig.show()


def exibir_relatorio():
    """Gera a interface de visualização no terminal."""
    print("==================================================")
    print("      SISTEMA QUANTITATIVO - BACKTEST RUNNER      ")
    print("==================================================\n")

    opcoes = listar_estrategias_processadas()
    if not opcoes:
        print("Nenhuma estratégia encontrada na pasta data/strategies.")
        print("Certifique-se de rodar o 'main.py' primeiro.")
        return

    print("Estratégias disponíveis para análise:")
    for idx, (ativo, tempo, estrategia) in enumerate(opcoes):
        print(f"[{idx}] {ativo} ({tempo}) -> {estrategia}")

    try:
        escolha = int(input("\nDigite o número da estratégia que deseja analisar: "))
        selecionada = opcoes[escolha]
    except (ValueError, IndexError):
        print("Escolha inválida. Encerrando.")
        return

    entrada_capital = input("Digite o capital inicial simulado em R$ [Padrão: 10000]: ")
    try:
        capital_inicial = float(entrada_capital) if entrada_capital.strip() else 10000.0
    except ValueError:
        capital_inicial = 10000.0

    ativo, tempo, nome_estrategia = selecionada

    # --- DICIONÁRIO DE MULTIPLICADORES B3 ---
    multiplicador = 1.0  # Padrão para ações (1 ponto = 1 Real)
    if "WIN" in ativo:
        multiplicador = 0.20
    elif "WDO" in ativo:
        multiplicador = 10.00
    elif "IND" in ativo: # Índice Cheio
        multiplicador = 1.00
    elif "DOL" in ativo: # Dólar Cheio
        multiplicador = 50.00

    # Definimos que operaremos apenas 1 contrato/ação por padrão para simulação base
    qtd_contratos = 1

    print(f"\nRodando simulação para {ativo} com {nome_estrategia} a partir de R$ {capital_inicial:,.2f}...\n")
    print(f"Configuração do Ativo: {qtd_contratos} contrato(s) com multiplicador de R$ {multiplicador} por ponto.")
    
    # Repassamos o multiplicador para o motor de cálculo
    df_trades = rodar_backtest(ativo, tempo, nome_estrategia, RAW_DIR, STRATEGIES_DIR, multiplicador, qtd_contratos)

    if df_trades.empty:
        print("Nenhum trade foi finalizado no período testado.")
        return

    total_trades = len(df_trades)
    lucros = df_trades[df_trades["Resultado_R$"] > 0]
    prejuizos = df_trades[df_trades["Resultado_R$"] <= 0]
    
    win_rate = (len(lucros) / total_trades) * 100
    
    # Variáveis corrigidas para não usarem $ no nome
    maior_ganho_rs = df_trades["Resultado_R$"].max()
    maior_perda_rs = df_trades["Resultado_R$"].min()

    # --- SIMULAÇÃO DE CAIXA REAL ---
    # Somamos o dinheiro que entrou e saiu no caixa usando o acumulado (cumsum)
    df_trades["Capital_Acumulado"] = capital_inicial + df_trades["Resultado_R$"].cumsum()
    
    capital_final = df_trades["Capital_Acumulado"].iloc[-1]
    lucro_liquido_real = capital_final - capital_inicial
    retorno_sobre_capital = (lucro_liquido_real / capital_inicial) * 100

    # Drawdown calculado em cima do capital em Reais
    df_trades["Pico_Capital"] = df_trades["Capital_Acumulado"].cummax()
    df_trades["Drawdown_R$"] = df_trades["Capital_Acumulado"] - df_trades["Pico_Capital"]
    df_trades["Drawdown_%"] = (df_trades["Drawdown_R$"] / df_trades["Pico_Capital"]) * 100
    drawdown_maximo_pct = df_trades["Drawdown_%"].min()

    print("============= RELATÓRIO DE DESEMPENHO =============")
    print(f"Ativo / Tempo      : {ativo} ({tempo})")
    print(f"Estratégia         : {nome_estrategia}")
    print("---------------------------------------------------")
    print(f"Total de Operações : {total_trades}")
    print(f"Taxa de Acerto     : {win_rate:.2f}%")
    print("---------------------------------------------------")
    print(f"Capital Inicial    : R$ {capital_inicial:,.2f}")
    print(f"Capital Final      : R$ {capital_final:,.2f}")
    print(f"Lucro Líquido      : R$ {lucro_liquido_real:,.2f}")
    print(f"Retorno s/ Capital : {retorno_sobre_capital:.2f}%")
    print(f"Drawdown Máximo    : {drawdown_maximo_pct:.2f}%")
    print(f"Maior Gain (R$)    : R$ {maior_ganho_rs:,.2f}")
    print(f"Maior Loss (R$)    : R$ {maior_perda_rs:,.2f}")
    print("===================================================\n")

    plotar_desempenho(df_trades, ativo, tempo, nome_estrategia, capital_inicial)


if __name__ == "__main__":
    exibir_relatorio()