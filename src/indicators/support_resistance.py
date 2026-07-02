import os
import pandas as pd


def calcular(df, ativo, tempo_grafico, calc_dir, **kwargs):
    """
    Calcula os níveis de Suporte e Resistência baseados nas máximas e mínimas
    de uma janela móvel (Canais de Donchian / Pivot Points).
    """
    periodos = kwargs.get("periodos", 20)
    
    print(f"    -> Calculando Suporte e Resistência de {periodos} períodos para {ativo}...")

    # Instancia um DataFrame apenas para as saídas do indicador
    df_calc = pd.DataFrame(index=df.index)

    # Resistência: A maior máxima alcançada nos últimos N períodos
    df_calc["Resistance"] = df["High"].rolling(window=periodos).max()

    # Suporte: A menor mínima alcançada nos últimos N períodos
    df_calc["Support"] = df["Low"].rolling(window=periodos).min()

    # Média Central (Opcional - serve como um Pivot/ponto de equilíbrio)
    df_calc["Mid_Pivot"] = (df_calc["Resistance"] + df_calc["Support"]) / 2

    # Nome do arquivo conforme o padrão do seu ecossistema
    nome_saida = f"{ativo}_{tempo_grafico}_SUPRES_{periodos}.csv"
    caminho_saida = os.path.join(calc_dir, nome_saida)

    df_calc.to_csv(caminho_saida)
    print(f"       Salvo: {nome_saida}")