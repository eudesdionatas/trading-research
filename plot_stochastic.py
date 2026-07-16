import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plotar_estocastico(ativo, tempo_grafico, periodos_k, suavizacao_d, raw_dir, indicators_dir, dias_visuais=200):
    """
    Carrega os dados e plota os candles junto com o Oscilador Estocástico (%K e %D)
    em um subgráfico inferior, com marcas explícitas de 0, 20, 50, 80 e 100 no eixo Y.
    """
    print(f"Preparando visualização para {ativo} (Estocástico %K:{periodos_k}, %D:{suavizacao_d})...")

    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_ind = os.path.join(
        indicators_dir, f"{ativo}_{tempo_grafico}_STOCH_{periodos_k}_{suavizacao_d}.csv"
    )

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print(f"Erro: Arquivos não encontrados para Estocástico ({periodos_k}, {suavizacao_d}).")
        return

    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)
    df = df_raw.join(df_ind).dropna(subset=["Stoch_K", "Stoch_D"]).tail(dias_visuais)

    # Subgráficos: Painel 1 (Preço, 70% de altura), Painel 2 (Estocástico, 30% de altura)
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
    )

    # Candlesticks no Painel 1
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

    # Linha %K (Rápida - Azul) no Painel 2
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Stoch_K"],
            mode="lines",
            line=dict(color="deepskyblue", width=2),
            name="%K (Rápida)",
        ),
        row=2,
        col=1,
    )

    # Linha %D (Lenta/Sinal - Laranja) no Painel 2
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Stoch_D"],
            mode="lines",
            line=dict(color="orange", width=1.5, dash="dash"),
            name="%D (Sinal)",
        ),
        row=2,
        col=1,
    )

    # Linhas de limites (20, 50, 80) no Painel 2
    for limite in [20, 50, 80]:
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

    # --- MODIFICAÇÃO PRINCIPAL: Forçar o eixo Y a exibir os valores de sobrecompra/sobrevenda ---
    fig.update_yaxes(
        tickvals=[0, 20, 50, 80, 100],  # Força a exibição destes valores específicos
        range=[-5, 105],                # Dá um pequeno respiro no topo e fundo do painel
        row=2,
        col=1
    )

    fig.update_layout(
        title=f"Validação Visual: {ativo} - Oscilador Estocástico (%K={periodos_k}, %D={suavizacao_d})",
        yaxis_title="Preço (R$)",
        yaxis2_title="Estocástico (0-100)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=750,
    )

    fig.show()


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
    INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")

    plotar_estocastico("PETR4", "D1", 14, 3, RAW_DIR, INDICATORS_DIR)