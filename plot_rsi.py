import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plotar_rsi(ativo, tempo_grafico, periodos, raw_dir, indicators_dir, dias_visuais=200):
    """
    Carrega os dados e plota os candles junto com o RSI (Índice de Força Relativa)
    em um subgráfico inferior, com marcas explícitas de 0, 30, 50, 70 e 100 no eixo Y.
    """
    print(f"Preparando visualização para {ativo} (RSI {periodos} per)...")

    col_rsi = f"RSI_{periodos}"

    # 1. Definir caminhos dos arquivos baseados no seu padrão de salvamento
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_ind = os.path.join(
        indicators_dir, f"{ativo}_{tempo_grafico}_RSI_{periodos}.csv"
    )

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print(f"Erro: Arquivos não encontrados para o RSI ({periodos}).")
        print("Certifique-se de ter rodado o main.py primeiro com este indicador ativo.")
        return

    # 2. Carregar dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)

    # 3. Unificar os DataFrames pelo índice e limpar NaNs do aquecimento
    df = df_raw.join(df_ind).dropna(subset=[col_rsi])

    # Cortar para exibição visual para não sobrecarregar o navegador
    df = df.tail(dias_visuais)

    # 4. Criar subgráficos: Painel 1 (Preço, 70% de altura), Painel 2 (RSI, 30% de altura)
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
    )

    # Adicionar Candlesticks no Painel 1
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Preço",
            increasing_line_color="lime",
            decreasing_line_color="crimson",
        ),
        row=1,
        col=1,
    )

    # Adicionar Linha do RSI no Painel 2 (Tom roxo/médio clássico)
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[col_rsi],
            mode="lines",
            line=dict(color="mediumpurple", width=2),
            name=f"RSI ({periodos}p)",
        ),
        row=2,
        col=1,
    )

    # Adicionar Linhas Tracejadas de Limite (30, 50, 70) no Painel 2
    for limite in [30, 50, 70]:
        fig.add_shape(
            type="line",
            x0=df.index[0],
            y0=limite,
            x1=df.index[-1],
            y1=limite,
            line=dict(color="rgba(255, 255, 255, 0.2)", width=1, dash="dot"),
            row=2,
            col=1,
        )

    # --- Configurações do Eixo Y do RSI (Marcações explícitas e margem de respiro) ---
    fig.update_yaxes(
        tickvals=[0, 30, 50, 70, 100],  # Força a exibição destes valores específicos
        range=[-5, 105],                # Impede que as linhas 0 e 100 fiquem coladas na borda
        row=2,
        col=1
    )

    # 5. Layout geral do gráfico
    fig.update_layout(
        title=f"Validação Visual: {ativo} - Índice de Força Relativa (RSI {periodos} per)",
        yaxis_title="Preço (R$)",
        yaxis2_title="RSI (0-100)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=750,
    )

    # Renderizar no navegador
    fig.show()


# --- Execução do Script ---
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
    INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")

    # Parâmetros padrão para testar
    ativo_teste = "PETR4"
    tempo_grafico_teste = "D1"
    periodos_teste = 14

    plotar_rsi(ativo_teste, tempo_grafico_teste, periodos_teste, RAW_DIR, INDICATORS_DIR)