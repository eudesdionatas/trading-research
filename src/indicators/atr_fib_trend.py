import os
import numpy as np
import pandas as pd


def calcular(df, ativo, tempo_grafico, indicators_dir, **kwargs):
    """Calcula o ATR Fibonacci Trend Envelopes.

    Baseia-se em uma Média Móvel e multiplica o ATR para criar bandas.
    O rompimento das bandas define a tendência, e níveis de Fibonacci
    são projetados para mapear zonas de pullback.
    """
    # Emulando os parâmetros de input do MQL5
    ma_type = kwargs.get("ma_type", "SMMA")  # Opções: 'SMA', 'EMA', 'SMMA'
    ma_len = kwargs.get("ma_len", 100)
    atr_len = kwargs.get("atr_len", 100)
    atr_mult = kwargs.get("atr_mult", 3.0)

    print(f"    -> Calculando ATR Fib Trend ({ma_type} {ma_len}, ATR {atr_len}) para {ativo}...")

    # 1. Cálculo do True Range (TR)
    # Máximo entre: High-Low, abs(High-PrevClose), abs(Low-PrevClose)
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift(1)).abs()
    low_close = (df["Low"] - df["Close"].shift(1)).abs()
    
    # Concatenar as três séries e pegar o valor máximo por linha
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # 2. Cálculo do ATR
    # No MT5, o iATR clássico utiliza uma média móvel simples (SMA) do True Range
    atr = tr.rolling(window=atr_len).mean()

    # 3. Cálculo da Média Móvel (Basis)
    if ma_type == "SMA":
        ma = df["Close"].rolling(window=ma_len).mean()
    elif ma_type == "EMA":
        ma = df["Close"].ewm(span=ma_len, adjust=False).mean()
    elif ma_type == "SMMA":
        # SMMA (Smoothed MA) no Pandas equivale ao RMA com alpha = 1 / window
        ma = df["Close"].ewm(alpha=1/ma_len, adjust=False).mean()
    else:
        ma = df["Close"].rolling(window=ma_len).mean()

    # 4. Cálculo das Bandas (Upper e Lower)
    upper = ma + (atr * atr_mult)
    lower = ma - (atr * atr_mult)

    # 5. Avaliação da Tendência (BufferTrend)
    # Inicializa com NaN
    trend = pd.Series(np.nan, index=df.index)
    
    # Condições de rompimento (Fechamento cruzando as bandas ATR)
    trend.loc[df["Close"] > upper] = 1   # Tendência de Alta
    trend.loc[df["Close"] < lower] = -1  # Tendência de Baixa
    
    # Propagar a última tendência válida até ocorrer novo rompimento
    trend = trend.ffill().fillna(1) # Preenche o período de warm-up com 1 (Alta)

    # 6. Cálculo da Linha Base e Níveis de Fibonacci
    df_calc = pd.DataFrame(index=df.index)
    df_calc["Trend"] = trend
    
    # A base (100%) é a banda inferior na Alta e a banda superior na Baixa
    df_calc["Basis"] = np.where(trend == 1, lower, upper)
    
    # Range entre as bandas para calcular o percentual de retração
    rng = upper - lower
    
    # Níveis para Tendência de Alta (1)
    fib50_up = lower + rng * 0.5
    fib618_up = lower + rng * (1.0 - 0.618)
    fib786_up = lower + rng * (1.0 - 0.786)
    
    # Níveis para Tendência de Baixa (-1)
    fib50_dn = upper - rng * 0.5
    fib618_dn = upper - rng * (1.0 - 0.618)
    fib786_dn = upper - rng * (1.0 - 0.786)
    
    # Aplicando a condicional vetorizada para mapear os níveis corretos dependendo da tendência
    df_calc["Fib_0_5"] = np.where(trend == 1, fib50_up, fib50_dn)
    df_calc["Fib_0_618"] = np.where(trend == 1, fib618_up, fib618_dn)
    df_calc["Fib_0_786"] = np.where(trend == 1, fib786_up, fib786_dn)

    # Limpeza opcional do período inicial onde as médias ainda não têm cálculo (warm-up)
    # Retirando as colunas extras, deixamos apenas os valores necessários
    df_calc = df_calc.dropna()

    # 7. Salvamento do Arquivo
    nome_saida = f"{ativo}_{tempo_grafico}_ATRFIB_{ma_type}{ma_len}_ATR{atr_len}.csv"
    caminho_saida = os.path.join(indicators_dir, nome_saida)
    
    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")