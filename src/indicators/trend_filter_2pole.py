import os
import numpy as np
import pandas as pd


def calcular(df, ativo, tempo_grafico, indicators_dir, **kwargs):
    """Calcula o Trend Filter (2-Pole) Envelopes.

    Utiliza matemática de processamento de sinais digitais para rastrear
    a tendência com baixo lag, criando bandas dinâmicas baseadas no ATR.
    """
    # Parâmetros padrão do indicador
    length = kwargs.get("length", 20)
    damping = kwargs.get("damping", 0.1)
    bands_mult = kwargs.get("bands", 1.0)
    atr_period = 200  # Fixo no código original do MQL5

    print(f"    -> Calculando Trend Filter 2-Pole ({length}, {damping}) para {ativo}...")

    # 1. Constantes Matemáticas do Filtro
    omega = 2.0 * np.pi / length
    alpha = damping * omega
    beta = omega ** 2

    # 2. Cálculo do ATR de 200 períodos
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift(1)).abs()
    low_close = (df["Low"] - df["Close"].shift(1)).abs()
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=atr_period).mean()

    # 3. Algoritmo do Filtro de 2 Polos usando Pandas EWM (Vetorizado)
    # Emulação de F1
    f1 = df["Close"].ewm(alpha=alpha, adjust=False).mean()
    # Emulação de F2 (TPF) aplicando a segunda suavização sobre F1
    tpf = f1.ewm(alpha=beta, adjust=False).mean()

    # Inicializando o DataFrame do indicador
    df_calc = pd.DataFrame(index=df.index)
    df_calc["TPF"] = tpf

    # 4. Determinação de Direção (Tendência)
    # Compara a inclinação do filtro com 2 barras atrás
    trend = pd.Series(np.nan, index=df.index)
    
    trend.loc[tpf > tpf.shift(2)] = 1
    trend.loc[tpf < tpf.shift(2)] = -1
    
    # ffill() mantém o estado anterior caso o valor seja exatamente igual (plano)
    trend = trend.ffill().fillna(1)
    df_calc["Trend"] = trend

    # 5. Cálculo das Margens Contínuas (Canais baseados no ATR)
    offset = atr * bands_mult
    
    # Lower_Band existe apenas na tendência de Alta (1)
    df_calc["Lower_Band"] = np.where(trend == 1, tpf - offset, np.nan)
    
    # Upper_Band existe apenas na tendência de Baixa (-1)
    df_calc["Upper_Band"] = np.where(trend == -1, tpf + offset, np.nan)

    # 6. Limpeza e Salvamento
    # Removemos apenas as linhas onde o próprio TPF é nulo (início do gráfico)
    # Não usamos df_calc.dropna() puro porque as colunas de Bandas contêm NaNs por design
    df_calc = df_calc.dropna(subset=["TPF", "Trend"])

    nome_saida = f"{ativo}_{tempo_grafico}_2POLE_{length}_{damping}.csv"
    caminho_saida = os.path.join(indicators_dir, nome_saida)
    
    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")