import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def plotar_2pole(ativo, tempo_grafico, length, damping, raw_dir, indicators_dir, dias_visuais=250):
    """
    Carrega os dados e plota o Trend Filter (2-Pole) interativo.
    Destaca a mudança de cor da linha central e plota as bandas alternadas.
    """
    print(f"Preparando visualização do Filtro de 2 Polos para {ativo}...")

    # 1. Definir caminhos
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    nome_ind = f"{ativo}_{tempo_grafico}_2POLE_{length}_{damping}.csv"
    arq_ind = os.path.join(indicators_dir, nome_ind)

    if not os.path.exists(arq_raw) or not os.path.exists(arq_ind):
        print(f"Erro: Arquivos não encontrados. Verifique se rodou o main.py para {nome_ind}")
        return

    # 2. Carregar e unificar os dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_ind, parse_dates=True, index_col=0)
    
    # Junta os dados e remove o período inicial onde o filtro estava se calibrando
    df = df_raw.join(df_ind).dropna(subset=["TPF"])
    
    # Cortar para focar na movimentação recente
    df = df.tail(dias_visuais)

    # 3. Preparar a linha central (TPF) com duas cores dependendo da tendência
    tpf_up = df['TPF'].copy()
    tpf_up.loc[df['Trend'] == -1] = np.nan  # Oculta nos momentos de baixa

    tpf_dn = df['TPF'].copy()
    tpf_dn.loc[df['Trend'] == 1] = np.nan   # Oculta nos momentos de alta

    # 4. Criar a figura interativa
    fig = go.Figure()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Preço', increasing_line_color='lime', decreasing_line_color='crimson'
    ))

    # Linha Central (Filtro 2-Polos) - Tendência de Alta (Verde Limão)
    fig.add_trace(go.Scatter(
        x=df.index, y=tpf_up, mode='lines',
        line=dict(color='lime', width=3), name='2-Pole Filter (Alta)'
    ))

    # Linha Central (Filtro 2-Polos) - Tendência de Baixa (Vermelho)
    fig.add_trace(go.Scatter(
        x=df.index, y=tpf_dn, mode='lines',
        line=dict(color='red', width=3), name='2-Pole Filter (Baixa)'
    ))

    # Banda Inferior (Suporte Contínuo na Alta) - Pontilhado Verde
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Lower_Band'], mode='lines',
        line=dict(color='lime', width=1.5, dash='dot'), name='Lower Band (Suporte)'
    ))

    # Banda Superior (Resistência Contínua na Baixa) - Pontilhado Vermelho
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Upper_Band'], mode='lines',
        line=dict(color='red', width=1.5, dash='dot'), name='Upper Band (Resistência)'
    ))

    # 5. Configurar layout visual
    fig.update_layout(
        title=f"Validação Visual: {ativo} - Trend Filter 2-Pole ({length}, damping={damping})",
        yaxis_title="Preço (R$)",
        xaxis_title="Data",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=750,
        hovermode="x unified"
    )

    fig.show()

# --- Execução ---
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
    INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
    
    # Parâmetros padrão usados na conversão
    plotar_2pole(
        ativo="PETR4", 
        tempo_grafico="D1", 
        length=20, 
        damping=0.1, 
        raw_dir=RAW_DIR, 
        indicators_dir=INDICATORS_DIR
    )