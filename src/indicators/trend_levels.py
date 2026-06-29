import os
import numpy as np
import pandas as pd


def calcular(df, ativo, tempo_grafico, indicators_dir, **kwargs):
    """Calcula o indicador Trend Levels (ChartPrime) convertendo a lógica do MQL5.

    Baseia-se no rompimento de máximas e mínimas locais para definir tendência
    e cria níveis dinâmicos (Upper, Lower, Mid) durante a duração do bloco de tendência.
    """
    # Emulando a variável 'InpLength' do MQL5
    periodos = kwargs.get("periodos", 30)

    print(f"    -> Calculando Trend Levels (ChartPrime) de {periodos} períodos para {ativo}...")

    df_calc = pd.DataFrame(index=df.index)
    
    # Trazemos High e Low temporariamente para facilitar os cálculos
    df_calc["High"] = df["High"]
    df_calc["Low"] = df["Low"]
    df_calc["Close"] = df["Close"]

    # 1. Encontrar a maior máxima e menor mínima dos últimos N períodos (InpLength)
    # Isso substitui o loop 'for(int j = 1; j < InpLength; j++)' do MQL5
    rolling_high = df_calc["High"].rolling(window=periodos).max()
    rolling_low = df_calc["Low"].rolling(window=periodos).min()

    # 2. Avaliação de quebra/reversão de tendência (BufTrend)
    # No MQL5, alta confirmada se high[i] == highest_n
    is_new_high = df_calc["High"] == rolling_high
    is_new_low = df_calc["Low"] == rolling_low

    df_calc["Trend"] = np.nan
    df_calc.loc[is_new_high, "Trend"] = 1   # Tendência de Alta
    df_calc.loc[is_new_low, "Trend"] = -1   # Tendência de Baixa
    
    # ffill() propaga a última tendência válida até que ocorra uma nova quebra.
    # Substitui a lógica: BufTrend[i] = BufTrend[i-1]
    df_calc["Trend"] = df_calc["Trend"].ffill().fillna(1)

    # 3. Gerenciamento do ciclo de contagem do bloco de tendência
    # Identificamos exatamente o momento da virada (BufTrend[i] != BufTrend[i-1])
    df_calc["Trend_Change"] = df_calc["Trend"] != df_calc["Trend"].shift(1)
    
    # Criamos um "ID de Bloco" que soma 1 toda vez que a tendência vira.
    # Isso nos permite agrupar os candles da tendência atual para achar os níveis.
    df_calc["Block_ID"] = df_calc["Trend_Change"].cumsum()

    # 4. Calcular Máxima, Mínima e Média com base no bloco atual (BufH1, BufL1, BufM1)
    # Substitui o loop 'for(int k = 1; k < current_bars; k++)'
    df_calc["Upper_Level"] = df_calc.groupby("Block_ID")["High"].cummax()
    df_calc["Lower_Level"] = df_calc.groupby("Block_ID")["Low"].cummin()
    df_calc["Mid_Level"] = (df_calc["Upper_Level"] + df_calc["Lower_Level"]) / 2.0

    # Opcional: Estatísticas do MQL5 (BufCountUp, BufCountDn)
    # Conta quantos fechamentos ocorreram acima ou abaixo do Mid_Level no bloco atual
    df_calc["Is_Above_Mid"] = (df_calc["Close"] > df_calc["Mid_Level"]).astype(int)
    df_calc["Is_Below_Mid"] = (df_calc["Close"] < df_calc["Mid_Level"]).astype(int)
    
    df_calc["Count_Up"] = df_calc.groupby("Block_ID")["Is_Above_Mid"].cumsum()
    df_calc["Count_Dn"] = df_calc.groupby("Block_ID")["Is_Below_Mid"].cumsum()

    # 5. Geração de Sinais de Virada (BufArrowsUp, BufArrowsDown)
    df_calc["Signal"] = 0
    df_calc.loc[(df_calc["Trend"] == 1) & (df_calc["Trend_Change"]), "Signal"] = 1
    df_calc.loc[(df_calc["Trend"] == -1) & (df_calc["Trend_Change"]), "Signal"] = -1

    # 6. Limpeza e Salvamento
    # Removemos as colunas auxiliares para deixar o arquivo final limpo
    colunas_remover = ["High", "Low", "Close", "Trend_Change", "Block_ID", "Is_Above_Mid", "Is_Below_Mid"]
    df_calc = df_calc.drop(columns=colunas_remover)

    # Nome e salvamento
    nome_saida = f"{ativo}_{tempo_grafico}_TRENDLEVELS_{periodos}.csv"
    caminho_saida = os.path.join(indicators_dir, nome_saida)
    df_calc.to_csv(caminho_saida)
    
    print(f"       Salvo: {nome_saida}")