import os
import pandas as pd


def calcular(df, ativo, tempo_grafico, calc_dir, **kwargs):
    """Calcula o RSI (Índice de Força Relativa) tradicional de 14 períodos

    e salva o resultado na pasta calc.
    """
    periodos = kwargs.get("periodos", 14)
    coluna_calculo = "Close"

    print(f"    -> Calculando RSI de {periodos} períodos para {ativo}...")

    df_calc = pd.DataFrame(index=df.index)

    # 1. Calcular as variações de preço de um dia para o outro
    delta = df[coluna_calculo].diff()

    # 2. Separar ganhos (up) e perdas (down)
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)

    # 3. Calcular a média exponencial dos ganhos e das perdas (padrão Wilder)
    ma_up = up.ewm(com=periodos - 1, adjust=False).mean()
    ma_down = down.ewm(com=periodos - 1, adjust=False).mean()

    # 4. Calcular a Força Relativa (RS) e o RSI
    rs = ma_up / ma_down
    df_calc[f"RSI_{periodos}"] = 100 - (100 / (1 + rs))

    # Tratar divisões por zero caso o mercado fique estagnado
    df_calc[f"RSI_{periodos}"] = df_calc[f"RSI_{periodos}"].fillna(50)

    # Salvar
    nome_saida = f"{ativo}_{tempo_grafico}_RSI_{periodos}.csv"
    caminho_saida = os.path.join(calc_dir, nome_saida)
    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")