import os
import numpy as np
import pandas as pd


def executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir, **kwargs):
    """Gera sinais de compra/venda baseados no Golden Pocket do ATR Fib."""
    
    # Recebendo os parâmetros dinâmicos (com valores padrão caso não sejam passados)
    ma_type = kwargs.get("ma_type", "SMMA")
    ma_len = kwargs.get("ma_len", 100)
    atr_len = kwargs.get("atr_len", 100)

    # Nome da estratégia agora reflete os parâmetros testados
    nome_estrategia = f"PULLBACK_ATRFIB_{ma_type}{ma_len}_ATR{atr_len}"

    # 1. Caminhos dos arquivos dinâmicos
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    nome_ind = f"{ativo}_{tempo_grafico}_ATRFIB_{ma_type}{ma_len}_ATR{atr_len}.csv"
    arq_atrfib = os.path.join(indicators_dir, nome_ind)

    if not os.path.exists(arq_raw) or not os.path.exists(arq_atrfib):
        return # Falha silenciosa para não poluir o terminal durante a otimização em massa

    # 2. Carregar e unificar os dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_ind = pd.read_csv(arq_atrfib, parse_dates=True, index_col=0)
    df = df_raw.join(df_ind).dropna(subset=["Basis"])

    # 3. Mapear o fechamento e as zonas do candle ANTERIOR
    prev_close = df["Close"].shift(1)
    prev_trend = df["Trend"].shift(1)
    prev_basis = df["Basis"].shift(1)
    
    prev_gp_top = df[["Fib_0_618", "Fib_0_786"]].shift(1).max(axis=1)
    prev_gp_bot = df[["Fib_0_618", "Fib_0_786"]].shift(1).min(axis=1)

    # 4. Regras de Sinal
    cond_compra = (prev_trend == 1) & (prev_close <= prev_gp_top) & (prev_close > prev_basis)
    cond_venda = (prev_trend == -1) & (prev_close >= prev_gp_bot) & (prev_close < prev_basis)

    df["Sinal"] = 0
    df.loc[cond_compra, "Sinal"] = 1
    df.loc[cond_venda, "Sinal"] = -1

    # 5. Definir Entradas, Stop Loss e Take Profit
    df["Preco_Entrada"] = df["Open"]
    df["Stop_Loss"] = np.nan
    df["Take_Profit"] = np.nan

    # Alvos de Compra
    df.loc[df["Sinal"] == 1, "Stop_Loss"] = prev_basis
    risco_compra = df["Preco_Entrada"] - df["Stop_Loss"]
    df.loc[df["Sinal"] == 1, "Take_Profit"] = df["Preco_Entrada"] + (risco_compra * 2)

    # Alvos de Venda
    df.loc[df["Sinal"] == -1, "Stop_Loss"] = prev_basis
    risco_venda = df["Stop_Loss"] - df["Preco_Entrada"]
    df.loc[df["Sinal"] == -1, "Take_Profit"] = df["Preco_Entrada"] - (risco_venda * 2)

    # 6. Salvar dados limpos
    colunas_salvar = ["Sinal", "Preco_Entrada", "Stop_Loss", "Take_Profit"]
    df_final = df[colunas_salvar]

    nome_saida = f"{ativo}_{tempo_grafico}_{nome_estrategia}.csv"
    caminho_saida = os.path.join(strategies_dir, nome_saida)
    df_final.to_csv(caminho_saida)