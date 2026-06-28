import pandas as pd

caminho_csv = "data/raw/PETR4.csv"

def carregar_dados(caminho_csv):
    """Carrega os dados históricos e garante a ordenação cronológica."""
    df = pd.read_csv(caminho_csv, parse_dates=True, index_col=0)
    df = df.sort_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    return df


def calcular_medias_moveis(df):
    """Calcula as médias móveis aritméticas de 11 e 40 períodos

    baseadas no Fechamento Ajustado (Adj Close).
    """
    print("Calculando indicadores...")

    # Média Móvel Simples (SMA) de 11 períodos
    df["MA_11"] = df["Adj Close"].rolling(window=11).mean()

    # Média Móvel Simples (SMA) de 40 períodos
    df["MA_40"] = df["Adj Close"].rolling(window=40).mean()

    return df


# --- Execução do Projeto ---
if __name__ == "__main__":
    arquivo = "data/raw/PETR4.csv"

    # 1. Carregar
    df_projeto = carregar_dados(arquivo)

    # 2. Calcular Indicadores
    df_projeto = calcular_medias_moveis(df_projeto)

    # Visualizando o resultado final com as novas colunas
    print("\n--- DataFrame Atualizado (Últimos dias) ---")
    colunas_historico = ["Adj Close", "MA_11", "MA_40"]
    print(df_projeto[colunas_historico].tail(10))

    # Opcional: Verificar as primeiras linhas para notar o efeito do "Warm-up"
    print("\n--- DataFrame Atualizado (Primeiros dias) ---")
    print(df_projeto[colunas_historico].head(15))