
import os
import pandas as pd
import plotly.graph_objects as go


def plotar_ema(ativo, tempo_grafico, periodos, raw_dir, calc_dir, dias_visuais=250):
    """
    Carrega os dados brutos e os dados do indicador Média Móvel Exponencial (EMA), 
    junta-os e plota um gráfico interativo com o Candlestick e a linha da EMA.
    """
    print(f"Preparando visualização para {ativo} (EMA {periodos} per)...")

    coluna_ema = f"EMA_{periodos}"

    # 1. Definir caminhos dos arquivos (buscando da pasta calc conforme seu padrão)
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_ind = os.path.join(calc_dir, f"{ativo}_{tempo_grafico}_EMA_{periodos}.csv")

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print("Erro: Arquivos não encontrados. Certifique-se de ter gerado a EMA primeiro.")
        return

    # 2. Carregar dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)

    # 3. Unificar os DataFrames pelo índice de data e limpar NaNs do período de aquecimento
    df = df_raw.join(df_ind).dropna(subset=[coluna_ema])

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

    # Adicionar a linha da EMA (Linha Amarela Ouro para se destacar bem no fundo escuro)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[coluna_ema],
        mode='lines',
        line=dict(color='gold', width=2),
        name=f'EMA {periodos}'
    ))

    # 5. Configurar layout visual do gráfico
    fig.update_layout(
        title=f"Validação Visual: {ativo} - Média Móvel Exponencial ({periodos} per)",
        yaxis_title="Preço (R$)",
        xaxis_title="Data",
        xaxis_rangeslider_visible=False, # Oculta a barra de rolagem inferior para limpar a tela
        template="plotly_dark", # Tema escuro padrão do seu ecossistema
        height=700
    )

    # Renderizar gráfico no navegador/notebook
    fig.show()


# --- Execução do Script ---
if __name__ == "__main__":
    # Ajuste os caminhos conforme a sua estrutura de pastas local
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
    CALC_DIR = os.path.join(BASE_DIR, "data", "indicators")  # Aponta para a pasta calc onde salvamos a EMA
    
    # Parâmetros para testar
    ativo_teste = "PETR4"
    tempo_grafico_teste = "D1"
    periodos_teste = 17
    
    plotar_ema(ativo_teste, tempo_grafico_teste, periodos_teste, RAW_DIR, CALC_DIR)