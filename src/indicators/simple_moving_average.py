import os
import pandas as pd


def calcular(df, ativo, tempo_grafico, calc_dir, **kwargs):
    """Calcula a Média Móvel e salva o arquivo específico na pasta calc."""
    periodos = kwargs.get("periodos", 20)
    coluna_calculo = "Close"

    print(f"    -> Calculando Média Móvel de {periodos} períodos para {ativo}...")

    # Instancia um DataFrame apenas com o resultado do indicador
    df_calc = pd.DataFrame(index=df.index)
    df_calc[f"SMA_{periodos}"] = (
        df[coluna_calculo].rolling(window=periodos).mean()
    )

    # Nome do arquivo conforme seu padrão: NOME-DO-ATIVO_TEMPO-GRÁFICO_INDICADOR_VALORES.csv
    nome_saida = f"{ativo}_{tempo_grafico}_SMA_{periodos}.csv"
    caminho_saida = os.path.join(calc_dir, nome_saida)

    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")