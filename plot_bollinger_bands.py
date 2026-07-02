import os
import pandas as pd
import plotly.graph_objects as go


def plotar_bollinger(ativo, tempo_grafico, periodos, desvios, raw_dir, indicators_dir, dias_visuais=400):
    """
    Carrega os dados brutos e os dados do indicador Bandas de Bollinger,
    junta-os e plota o gráfico interativo para validação visual.
    """
    print(f"Preparando visualização para {ativo} (Bandas de Bollinger {periodos} per, {desvios} desv)...")

    # Mapeamento dos nomes das colunas conforme o arquivo de cálculo gerou
    col_centro = f"BB_Centro_{periodos}"
    col_superior = f"BB_Superior_{periodos}_{desvios}"
    col_inferior = f"BB_Inferior_{periodos}_{desvios}"

    # 1. Definir caminhos dos arquivos baseados no seu padrão de salvamento
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_ind = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_BB_{periodos}_{desvios}.csv")

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print(f"Erro: Arquivos não encontrados para BB ({periodos}, {desvios}).")
        print("Certifique-se de ter rodado o main.py primeiro com este indicador ativo.")
        return

    # 2. Carregar dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)

    # 3. Unificar os DataFrames pelo índice e limpar NaNs do aquecimento
    df = df_raw.join(df_ind).dropna(subset=[col_centro])

    # Cortar para exibição visual para não pesar o navegador
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

    # Adicionar Banda Superior (Linha sutil cinza/clara)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[col_superior],
        mode='lines',
        line=dict(color='rgba(173, 181, 189, 0.8)', width=1.5),
        name='Banda Superior'
    ))

    # Adicionar Banda Central / Média Móvel (Linha tracejada azul-clara)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[col_centro],
        mode='lines',
        line=dict(color='deepskyblue', width=1.5, dash='dash'),
        name='Banda Central (MMS)'
    ))

    # Adicionar Banda Inferior (Linha sutil cinza/clara)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[col_inferior],
        mode='lines',
        line=dict(color='rgba(173, 181, 189, 0.8)', width=1.5),
        name='Banda Inferior'
    ))

    # 5. Configurar layout visual do gráfico
    fig.update_layout(
        title=f"Validação Visual: {ativo} - Bandas de Bollinger ({periodos} per, {desvios} desv)",
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
    
    # IMPORTANTE: Mude para a pasta onde suas BBs estão salvando (calc ou indicators)
    # Conforme vimos nos seus testes, seu pipeline atual joga tudo em 'indicators'
    INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
    
    # Parâmetros para testar
    ativo_teste = "PETR4"
    tempo_grafico_teste = "D1"
    periodos_teste = 20
    desvios_teste = 2
    
    plotar_bollinger(ativo_teste, tempo_grafico_teste, periodos_teste, desvios_teste, RAW_DIR, INDICATORS_DIR)