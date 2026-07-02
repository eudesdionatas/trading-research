import os
import pandas as pd
import plotly.graph_objects as go


def plotar_suporte_resistencia(ativo, tempo_grafico, periodos, raw_dir, indicators_dir, dias_visuais=200):
    """
    Carrega os dados brutos e os dados do indicador Suporte/Resistência,
    junta-os e plona o gráfico interativo para validação visual.
    """
    print(f"Preparando visualização para {ativo} (Suporte/Resistência {periodos} per)...")

    # 1. Definir caminhos dos arquivos baseados no padrão gerado
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_ind = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_SUPRES_{periodos}.csv")

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print(f"Erro: Arquivos não encontrados para o período {periodos}.")
        print("Certifique-se de ter rodado o main.py primeiro com este indicador ativo.")
        return

    # 2. Carregar dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)

    # 3. Unificar os DataFrames pelo índice
    df = df_raw.join(df_ind).dropna(subset=["Resistance", "Support"])

    # Cortar para exibição visual
    df = df.tail(dias_visuais)

    # 4. Criar a figura do Plotly
    fig = go.Figure()

    # Adicionar os Candlesticks de Preço
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

    # Adicionar Linha de Resistência (Vermelho/Tom de Alerta)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df["Resistance"],
        mode='lines',
        line=dict(color='tomato', width=2),
        name=f'Resistência ({periodos} p)'
    ))

    # Adicionar Linha de Suporte (Verde Claro/Tom de Compra)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df["Support"],
        mode='lines',
        line=dict(color='mediumspringgreen', width=2),
        name=f'Suporte ({periodos} p)'
    ))

    # Adicionar Linha do Pivot Central (Linha fina pontilhada cinza)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df["Mid_Pivot"],
        mode='lines',
        line=dict(color='rgba(200, 200, 200, 0.5)', width=1, dash='dash'),
        name='Pivot Central'
    ))

    # 5. Configurar layout visual do gráfico
    fig.update_layout(
        title=f"Validação Visual: {ativo} - Suporte e Resistência ({periodos} per)",
        yaxis_title="Preço (R$)",
        xaxis_title="Data",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=700
    )

    # Renderizar gráfico no navegador
    fig.show()


# --- Execução do Script ---
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
    INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
    
    # Parâmetros para testar (mude se rodar outros ativos ou períodos no main)
    ativo_teste = "PETR4"
    tempo_grafico_teste = "D1"
    periodos_teste = 20
    
    plotar_suporte_resistencia(ativo_teste, tempo_grafico_teste, periodos_teste, RAW_DIR, INDICATORS_DIR)