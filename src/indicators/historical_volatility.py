import os
import numpy as np
import pandas as pd


def calcular(df, ativo, tempo_grafico, indicators_dir, **kwargs):
    """Calcula a Volatilidade Histórica Anualizada utilizando retornos logarítmicos

    e salva o resultado na pasta de indicadores.
    """
    periodos = kwargs.get("periodos", 20)
    dias_ano = kwargs.get("dias_ano", 252)  # Dias úteis padrão para ações/REITs

    print(
        f"    -> Calculando Volatilidade Histórica ({periodos} per) para {ativo}..."
    )

    df_calc = pd.DataFrame(index=df.index)

    # 1. Calcular os retornos logarítmicos baseados no Fechamento (Close)
    df_calc["Log_Returns"] = np.log(df["Close"] / df["Close"].shift(1))

    # 2. Calcular o desvio padrão móvel dos retornos logarítmicos
    desvio_movel = df_calc["Log_Returns"].rolling(window=periodos).std()

    # 3. Anualizar a volatilidade multiplicando pela raiz quadrada dos dias úteis (multiplicado por 100 para virar %)
    df_calc[f"Vol_Historica_{periodos}"] = (
        desvio_movel * np.sqrt(dias_ano) * 100
    )

    # Limpar a coluna temporária de retornos antes de salvar
    df_calc = df_calc.drop(columns=["Log_Returns"])

    # Salvar conforme o padrão do seu ecossistema
    nome_saida = f"{ativo}_{tempo_grafico}_VOLHIST_{periodos}.csv"
    caminho_saida = os.path.join(indicators_dir, nome_saida)

    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")