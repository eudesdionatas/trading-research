import os
import pandas as pd


def executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir):
    """Executa a estratégia de Cruzamento de Médias Móveis (11 vs 35) filtrada pelo RSI."""
    nome_estrategia = "CROSSOVER_EMA_11_35_RSI_14"
    print(f"    -> Rodando estratégia {nome_estrategia} para {ativo}...")

    # 1. Mapear caminhos dos arquivos necessários
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_ma11 = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_EMA_11.csv")
    arq_ma35 = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_EMA_35.csv")  # Corrigido para 35
    arq_rsi = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_RSI_14.csv")

    # Verificação de segurança
    for arq in [arq_raw, arq_ma11, arq_ma35, arq_rsi]:
        if not os.path.exists(arq):
            print(f"       [Erro] Arquivo necessário não encontrado: {os.path.basename(arq)}")
            return

    # 2. Carregar e unificar temporariamente para calcular a lógica
    df = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ma11 = pd.read_csv(arq_ma11, parse_dates=True, index_col=0)
    df_ma35 = pd.read_csv(arq_ma35, parse_dates=True, index_col=0)
    df_rsi = pd.read_csv(arq_rsi, parse_dates=True, index_col=0)

    df["EMA_11"] = df_ma11["EMA_11"]
    df["EMA_35"] = df_ma35["EMA_35"]
    df["RSI_14"] = df_rsi["RSI_14"]

    # Remover NaNs do início para evitar sinais falsos no aquecimento das médias
    df = df.dropna()

    # 3. Lógica Quantitativa
    df["Cruzou_Acima"] = (df["EMA_11"] > df["EMA_35"]) & (df["EMA_11"].shift(1) <= df["EMA_35"].shift(1))
    df["Cruzou_Abaixo"] = (df["EMA_11"] < df["EMA_35"]) & (df["EMA_11"].shift(1) >= df["EMA_35"].shift(1))

    # Inicializa a coluna de sinais
    df["Sinal"] = 0

    # COMPRA (1): Média de 11 cruzou para cima a de 35 E RSI < 70
    df.loc[df["Cruzou_Acima"] & (df["RSI_14"] < 70), "Sinal"] = 1

    # VENDA (-1): Média de 11 cruzou para baixo a de 35
    df.loc[df["Cruzou_Abaixo"], "Sinal"] = -1

    # 4. SALVAMENTO LEVE: Filtrando apenas a coluna desejada (o índice de Data vai junto automaticamente)
    df_sinal_puro = df[["Sinal"]]

    nome_saida = f"{ativo}_{tempo_grafico}_{nome_estrategia}.csv"
    caminho_saida = os.path.join(strategies_dir, nome_saida)
    df_sinal_puro.to_csv(caminho_saida)

    print(f"       Sinal salvo com sucesso: {nome_saida}")