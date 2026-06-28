import os
import pandas as pd


def calcular(df, ativo, tempo_grafico, calc_dir, **kwargs):
    """Calcula o MACD clássico (Fast=12, Slow=26, Sinal=9) e salva na pasta calc."""
    fast = kwargs.get("fast", 12)
    slow = kwargs.get("slow", 26)
    sinal = kwargs.get("sinal", 9)
    coluna_calculo = "Close"

    print(
        f"    -> Calculando MACD ({fast}, {slow}, {sinal}) para {ativo}..."
    )

    df_calc = pd.DataFrame(index=df.index)

    # 1. Calcular as Médias Móveis Exponenciais (EMA) curta e longa
    ema_fast = df[coluna_calculo].ewm(span=fast, adjust=False).mean()
    ema_slow = df[coluna_calculo].ewm(span=slow, adjust=False).mean()

    # 2. Linha MACD (Diferença entre as duas EMAs)
    df_calc[f"MACD_Linha_{fast}_{slow}"] = ema_fast - ema_slow

    # 3. Linha de Sinal (EMA da própria linha MACD)
    df_calc[f"MACD_Sinal_{sinal}"] = (
        df_calc[f"MACD_Linha_{fast}_{slow}"].ewm(span=sinal, adjust=False).mean()
    )

    # 4. Histograma MACD
    df_calc[f"MACD_Hist_{fast}_{slow}_{sinal}"] = (
        df_calc[f"MACD_Linha_{fast}_{slow}"] - df_calc[f"MACD_Sinal_{sinal}"]
    )

    # Salvar
    nome_saida = f"{ativo}_{tempo_grafico}_MACD_{fast}_{slow}_{sinal}.csv"
    caminho_saida = os.path.join(calc_dir, nome_saida)
    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")