import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração de caminhos globais (Padrão do projeto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")

def plotar_indicador_atr(ativo, tempo_grafico, periodo=14):
    """
    Gera um gráfico do preço do ativo (Candlestick) e um painel inferior
    mostrando a oscilação do indicador ATR.
    """
    print(f"-> Carregando dados para plotagem do ATR de {ativo} ({tempo_grafico})...")
    
    # 1. Carregar Dados Brutos de Preço
    arq_raw = os.path.join(RAW_DIR, f"{ativo}_{tempo_grafico}.csv")
    if not os.path.exists(arq_raw):
        print(f"[Erro] Arquivo de preços não encontrado: {arq_raw}")
        return
    df = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df = df.sort_index()

    # 2. Carregar o Indicador ATR correspondente
    arq_atr = os.path.join(INDICATORS_DIR, f"{ativo}_{tempo_grafico}_ATR_{periodo}.csv")
    if not os.path.exists(arq_atr):
        print(f"[Erro] Arquivo do ATR não encontrado: {arq_atr}")
        return
    df_atr = pd.read_csv(arq_atr, parse_dates=True, index_col=0)
    
    # Cruzando os dados pelo índice temporal
    df[f"ATR_{periodo}"] = df_atr[f"ATR_{periodo}"]
    df = df.dropna()

    # 3. Configurar Subplots (Painel Superior: Preço | Painel Inferior: ATR)
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=(f"Preço de Fechamento / Candlestick - {ativo}", f"ATR ({periodo}) - Volatilidade Nominal"),
        row_heights=[0.7, 0.3]
    )

    # Gráfico Superior: Candlestick do Ativo
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Preço ($)"
    ), row=1, col=1)

    # Gráfico Inferior: Linha de Volatilidade do ATR
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[f"ATR_{periodo}"],
        mode='lines', 
        name=f'ATR ({periodo})', 
        line=dict(color='cyan', width=2),
        fill='tozeroy', 
        fillcolor='rgba(0, 255, 255, 0.05)' # Sombra sutil sob a linha
    ), row=2, col=1)

    # 4. Customização de Layout (Tema Escuro padrão do Backtester)
    fig.update_layout(
        title=f"Análise Estatística de Volatilidade: {ativo} ({tempo_grafico})",
        template="plotly_dark",
        height=750,
        xaxis_rangeslider_visible=False, # Remove o slider duplicado do candlestick
        hovermode="x unified",
        showlegend=True
    )
    
    # Forçar rótulos claros nos eixos $Y$
    fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volatilidade (R$ / Pontos)", row=2, col=1)

    # Exibir no navegador padrão
    fig.show()

if __name__ == "__main__":
    # Teste rápido de visualização para o seu ativo atual
    # Altere as variáveis abaixo conforme precisar avaliar outro timeframe ou ativo
    ATIVO_TESTE = "PETR4"
    TEMPO_TESTE = "D1"
    
    plotar_indicador_atr(ATIVO_TESTE, TEMPO_TESTE, periodo=14)