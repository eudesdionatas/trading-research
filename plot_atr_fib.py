import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def plotar_atr_fib(ativo, tempo_grafico, ma_type, ma_len, atr_len, raw_dir, indicators_dir, dias_visuais=250):
    """
    Carrega os dados e plota o ATR Fibonacci Trend Envelopes interativo,
    destacando a mudança de tendência e a Golden Pocket.
    """
    print(f"Preparando visualização do ATR Fib para {ativo}...")

    # 1. Definir caminhos
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    nome_ind = f"{ativo}_{tempo_grafico}_ATRFIB_{ma_type}{ma_len}_ATR{atr_len}.csv"
    arq_ind = os.path.join(indicators_dir, nome_ind)

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print(f"Erro: Arquivos não encontrados. Verifique se rodou o main.py para {nome_ind}")
        return

    # 2. Carregar e unificar os dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)
    
    df = df_raw.join(df_ind).dropna(subset=["Basis"])
    
    # Cortar para não pesar o navegador
    df = df.tail(dias_visuais)

    # 3. Preparar as linhas de tendência (para trocar a cor da base)
    # Criamos séries separadas para a linha Ciano (Alta) e Vermelha (Baixa)
    basis_up = df['Basis'].copy()
    basis_up.loc[df['Trend'] == -1] = np.nan  # Oculta nos momentos de baixa

    basis_dn = df['Basis'].copy()
    basis_dn.loc[df['Trend'] == 1] = np.nan   # Oculta nos momentos de alta

    # 4. Criar a figura
    fig = go.Figure()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Preço', increasing_line_color='lime', decreasing_line_color='crimson'
    ))

    # Linha Base (Tendência de Alta) - Ciano espesso
    fig.add_trace(go.Scatter(
        x=df.index, y=basis_up, mode='lines',
        line=dict(color='cyan', width=3), name='Base (Alta)'
    ))

    # Linha Base (Tendência de Baixa) - Vermelho espesso
    fig.add_trace(go.Scatter(
        x=df.index, y=basis_dn, mode='lines',
        line=dict(color='red', width=3), name='Base (Baixa)'
    ))

    # Nível Mid (Fib 0.5) - Pontilhado Cinza
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Fib_0_5'], mode='lines',
        line=dict(color='gray', width=1, dash='dot'), name='Fib 0.5 (Mid)'
    ))

    # Nível Fib 0.618 (Laranja)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Fib_0_618'], mode='lines',
        line=dict(color='orange', width=1.5), name='Fib 0.618'
    ))

    # Nível Fib 0.786 (Laranja com Preenchimento Golden Pocket)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Fib_0_786'], mode='lines',
        line=dict(color='orange', width=1.5),
        fill='tonexty', # Preenche o espaço até a linha desenhada imediatamente antes (0.618)
        fillcolor='rgba(255, 165, 0, 0.15)', # Laranja translúcido
        name='Fib 0.786 (Golden Pocket)'
    ))

    # 5. Configurar layout
    fig.update_layout(
        title=f"Validação Visual: {ativo} - ATR Fib Envelopes ({ma_type} {ma_len}, ATR {atr_len})",
        yaxis_title="Preço (R$)",
        xaxis_title="Data",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=750,
        hovermode="x unified" # Mostra todos os valores juntos ao passar o mouse
    )

    fig.show()

# --- Execução ---
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
    INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
    
    plotar_atr_fib(
        ativo="PETR4", 
        tempo_grafico="D1", 
        ma_type="SMMA", 
        ma_len=100, 
        atr_len=100, 
        raw_dir=RAW_DIR, 
        indicators_dir=INDICATORS_DIR
    )