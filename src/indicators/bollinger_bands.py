import os
import pandas as pd


def calcular(df, ativo, tempo_grafico, calc_dir, **kwargs):
    """Calcula as Bandas de Bollinger (Média de 20 períodos com 2 Desvios Padrão)

    e salva os resultados na pasta calc.
    """
    periodos = kwargs.get("periodos", 20)
    desvios = kwargs.get("desvios", 2)
    coluna_calculo = "Close"

    print(
        f"    -> Calculando Bandas de Bollinger ({periodos} per, {desvios} desv) para {ativo}..."
    )

    df_calc = pd.DataFrame(index=df.index)

    # 1. Banda Central (Média Móvel Simples)
    df_calc[f"BB_Centro_{periodos}"] = (
        df[coluna_calculo].rolling(window=periodos).mean()
    )

    # 2. Desvio Padrão do período
    desvio_padrao = df[coluna_calculo].rolling(window=periodos).std()

    # 3. Bandas Superior e Inferior
    df_calc[f"BB_Superior_{periodos}_{desvios}"] = (
        df_calc[f"BB_Centro_{periodos}"] + (desvio_padrao * desvios)
    )
    df_calc[f"BB_Inferior_{periodos}_{desvios}"] = (
        df_calc[f"BB_Centro_{periodos}"] - (desvio_padrao * desvios)
    )

    # Salvar
    nome_saida = f"{ativo}_{tempo_grafico}_BB_{periodos}_{desvios}.csv"
    caminho_saida = os.path.join(calc_dir, nome_saida)
    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")