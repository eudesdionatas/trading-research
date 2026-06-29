import os
import pandas as pd
import plotly.graph_objects as go

def plotar_trend_levels(ativo, tempo_grafico, periodos, raw_dir, indicators_dir, dias_visuais=200):
    """
    Carrega os dados brutos e os dados do indicador Trend Levels, 
    junta-os e plota um gráfico interativo.
    """
    print(f"Preparando visualização para {ativo}...")

    # 1. Definir caminhos dos arquivos
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_ind = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_TRENDLEVELS_{periodos}.csv")

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print("Erro: Arquivos não encontrados. Certifique-se de ter rodado o main.py primeiro.")
        return

    # 2. Carregar dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)

    # 3. Unificar os DataFrames pelo índice de data e limpar NaNs do período de aquecimento
    df = df_raw.join(df_ind).dropna(subset=["Upper_Level"])

    # Cortar o DataFrame para exibir apenas os últimos N dias (evita lentidão no navegador)
    df = df.tail(dias_visuais)

    # 4. Criar a figura do Plotly
    fig = go.Figure()

    # Adicionar os Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Preço',
        increasing_line_color='lime', 
        decreasing_line_color='crimson'
    ))

    # Adicionar Upper Level (Linha Azul Clara)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Upper_Level'],
        mode='lines',
        line=dict(color='deepskyblue', width=2),
        name='Upper Level'
    ))

    # Adicionar Lower Level (Linha Fúcsia)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Lower_Level'],
        mode='lines',
        line=dict(color='fuchsia', width=2),
        name='Lower Level'
    ))

    # Adicionar Mid Level (Linha Pontilhada Cinza)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Mid_Level'],
        mode='lines',
        line=dict(color='gray', width=1, dash='dot'),
        name='Mid Level'
    ))

    # Isolar pontos de Sinais para plotar os triângulos
    df_compra = df[df['Signal'] == 1]
    df_venda = df[df['Signal'] == -1]

    # Plotar Sinal de Compra (Triângulo Azul apontando para cima)
    fig.add_trace(go.Scatter(
        x=df_compra.index,
        y=df_compra['Low'] * 0.98, # Descola levemente do fundo do candle
        mode='markers',
        marker=dict(symbol='triangle-up', size=14, color='blue'),
        name='Sinal de Compra'
    ))

    # Plotar Sinal de Venda (Triângulo Vermelho apontando para baixo)
    fig.add_trace(go.Scatter(
        x=df_venda.index,
        y=df_venda['High'] * 1.02, # Descola levemente do topo do candle
        mode='markers',
        marker=dict(symbol='triangle-down', size=14, color='red'),
        name='Sinal de Venda'
    ))

    # 5. Configurar layout visual do gráfico
    fig.update_layout(
        title=f"Validação Visual: {ativo} - Trend Levels ChartPrime ({periodos} per)",
        yaxis_title="Preço (R$)",
        xaxis_title="Data",
        xaxis_rangeslider_visible=False, # Oculta a barra de rolagem inferior para limpar a tela
        template="plotly_dark", # Tema escuro para destacar as cores vivas
        height=700
    )

    # Renderizar gráfico no navegador/notebook
    fig.show()

# --- Execução do Script ---
if __name__ == "__main__":
    # Ajuste os caminhos abaixo conforme a sua estrutura de pastas local
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
    INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
    
    # Parâmetros para testar
    ativo_teste = "PETR4"
    tempo_grafico_teste = "D1"
    periodos_teste = 30
    
    plotar_trend_levels(ativo_teste, tempo_grafico_teste, periodos_teste, RAW_DIR, INDICATORS_DIR)