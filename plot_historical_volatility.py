import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plotar_volatilidade_historica(ativo, tempo_grafico, periodos, raw_dir, indicators_dir, dias_visuais=200):
    """Carrega os dados e plota o gráfico de candles com a volatilidade histórica

    em um subgráfico inferior para validação visual.
    """
    print(
        f"Preparando visualização para {ativo} (Volatilidade Histórica {periodos} per)..."
    )

    col_vol = f"Vol_Historica_{periodos}"

    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_ind = os.path.join(
        indicators_dir, f"{ativo}_{tempo_grafico}_VOLHIST_{periodos}.csv"
    )

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print(f"Erro: Arquivos não encontrados para VOLHIST ({periodos}).")
        return

    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)
    df = df_raw.join(df_ind).dropna(subset=[col_vol]).tail(dias_visuais)

    # Criar subgráficos: Painel 1 (Preço, 70% de altura), Painel 2 (Volatilidade, 30% de altura)
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

    # Adicionar Linha de Volatilidade Histórica no Painel 2
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[col_vol],
            mode="lines",
            line=dict(color="orchid", width=2),
            name=f"Vol. Histórica {periodos}p (%)",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        title=f"Validação Visual: {ativo} - Volatilidade Histórica Anualizada",
        yaxis_title="Preço (R$)",
        yaxis2_title="Volatilidade (%)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=750,
    )

    fig.show()


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
    INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")

    plotar_volatilidade_historica(
        "PETR4", "D1", 20, RAW_DIR, INDICATORS_DIR
    )