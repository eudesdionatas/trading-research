import os
import numpy as np
import pandas as pd


def executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir):
    """Estratégia RSI ATR Reversal:

    Entrada: Compra se RSI <= 20 | Venda se RSI >= 80
    Risco: Alvos dinâmicos baseados em ATR (Stop = 1.5 * ATR | Gain = 2.0 * Stop)
    """
    print(f"       -> Gerando sinais RSI ATR Extreme Reversal para {ativo}...")

    # 1. Carregar Dados Brutos de Preço
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    if not os.path.exists(arq_raw):
        print(f"       [Erro] Arquivo de preços não encontrado: {arq_raw}")
        return
    df = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df = df.sort_index()

    # 2. Carregar Indicador: RSI (Assumindo período padrão 14)
    arq_rsi = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_RSI_14.csv")
    if not os.path.exists(arq_rsi):
        print(f"       [Erro] Arquivo do RSI não encontrado: {arq_rsi}")
        return
    df_rsi = pd.read_csv(arq_rsi, parse_dates=True, index_col=0)
    df["RSI_14"] = df_rsi["RSI_14"]

    # 3. Carregar Indicador: ATR (Gerado no Passo 1 do pipeline)
    arq_atr = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_ATR_14.csv")
    if not os.path.exists(arq_atr):
        print(f"       [Erro] Arquivo do ATR não encontrado: {arq_atr}")
        return
    df_atr = pd.read_csv(arq_atr, parse_dates=True, index_col=0)
    df["ATR_14"] = df_atr["ATR_14"]

    # Limpar linhas com dados faltantes iniciais do cálculo dos indicadores
    df = df.dropna()

    # 4. Configuração dos Gatilhos do RSI
    # Compra na região de sobrevenda (<= 20) e Venda na região de sobrecompra (>= 80)
    df["Sinal"] = 0
    df.loc[df["RSI_14"] <= 20, "Sinal"] = 1  # 1 = Sinal de Compra
    df.loc[df["RSI_14"] >= 80, "Sinal"] = -1  # -1 = Sinal de Venda

    # 5. Cálculo Dinâmico de Alvos de Risco Baseados no ATR
    multiplicador_stop = 3

    # O ATR mensura a volatilidade diretamente em valor nominal (Reais)
    df["Stop_Loss"] = round(df["ATR_14"] * multiplicador_stop, 2)
    df["Take_Profit"] = round(df["Stop_Loss"] * 2.0, 2)  # Mantém proporção 2:1

    # Filtros de segurança mínimos para evitar divisões por zero ou alvos irrisórios
    df["Stop_Loss"] = df["Stop_Loss"].clip(lower=0.15)
    df["Take_Profit"] = df["Take_Profit"].clip(lower=0.30)

    # 6. Salvar DataFrame de Sinais para o Backtester consumir
    nome_saida = f"{ativo}_{tempo_grafico}_RSI_ATR_EXTREME_REVERSAL.csv"
    caminho_saida = os.path.join(strategies_dir, nome_saida)

    # Mantemos a estrutura de colunas que o motor `rodar_backtest` exige
    df_salvar = df[["Open", "High", "Low", "Close", "Sinal", "Stop_Loss", "Take_Profit"]]
    df_salvar.to_csv(caminho_saida)
    print(f"       Sinais salvos com sucesso em: {nome_saida}")