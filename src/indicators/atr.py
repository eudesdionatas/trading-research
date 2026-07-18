import os
import pandas as pd


def calcular(df, ativo, tempo_grafico, calc_dir, **kwargs):
    """
    Calcula o ATR (Average True Range) de 14 períodos (padrão Wilder)
    e salva o resultado na pasta de indicadores.
    """
    periodos = kwargs.get("periodos", 14)
    print(f"    -> Calculando ATR de {periodos} períodos para {ativo}...")

    df_calc = pd.DataFrame(index=df.index)

    # 1. Calcular as 3 distâncias potenciais do True Range (TR)
    max_min = df["High"] - df["Low"]
    max_close_ant = (df["High"] - df["Close"].shift(1)).abs()
    min_close_ant = (df["Low"] - df["Close"].shift(1)).abs()

    # 2. O True Range é o maior valor entre as 3 distâncias
    df_calc["True_Range"] = pd.concat([max_min, max_close_ant, min_close_ant], axis=1).max(axis=1)

    # 3. O ATR é a média móvel exponencial ponderada do TR (Média de Wilder)
    df_calc[f"ATR_{periodos}"] = df_calc["True_Range"].ewm(com=periodos - 1, adjust=False).mean()

    # Limpar a coluna intermediária de True Range antes de salvar
    df_saida = df_calc[[f"ATR_{periodos}"]]

    # Salvar seguindo seu padrão do pipeline
    nome_saida = f"{ativo}_{tempo_grafico}_ATR_{periodos}.csv"
    caminho_saida = os.path.join(calc_dir, nome_saida)
    df_saida.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")