import os
import pandas as pd


def calcular(df, ativo, tempo_grafico, indicators_dir, **kwargs):
    """
    Calcula o Oscilador Estocástico (%K e %D) e salva os resultados.
    
    Parâmetros padrão:
    - periodos_k (Janela de observação): 14 períodos
    - suavizacao_d (Média móvel para a linha de sinal %D): 3 períodos
    """
    periodos_k = kwargs.get("periodos_k", 14)
    suavizacao_d = kwargs.get("suavizacao_d", 3)

    print(
        f"    -> Calculando Oscilador Estocástico (%K: {periodos_k}, %D: {suavizacao_d}) para {ativo}..."
    )

    df_calc = pd.DataFrame(index=df.index)

    # 1. Obter a menor mínima e a maior máxima dos últimos N períodos
    menor_minima = df["Low"].rolling(window=periodos_k).min()
    maior_maxima = df["High"].rolling(window=periodos_k).max()

    # 2. Calcular a linha %K rápida
    # Fórmula: %K = 100 * ((Fechamento - Menor Mínima) / (Maior Máxima - Menor Mínima))
    df_calc["Stoch_K"] = (
        (df["Close"] - menor_minima) / (maior_maxima - menor_minima)
    ) * 100

    # 3. Calcular a linha %D lenta (Média Móvel Simples de %K)
    df_calc["Stoch_D"] = df_calc["Stoch_K"].rolling(window=suavizacao_d).mean()

    # Salvar conforme o padrão do seu ecossistema
    nome_saida = f"{ativo}_{tempo_grafico}_STOCH_{periodos_k}_{suavizacao_d}.csv"
    caminho_saida = os.path.join(indicators_dir, nome_saida)

    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")