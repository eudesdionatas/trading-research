import os
import numpy as np
import pandas as pd


def executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir):
    """
    Executa a estratégia de Reversão de Extremos do RSI (14 períodos).
    Compra quando RSI <= 20, Vende quando RSI >= 80.
    
    Os limites de Gain e Loss são dinâmicos e calculados com base 
    na Volatilidade Histórica de 20 períodos do ativo.
    """
    nome_estrategia = "RSI_EXTREME_REVERSAL_14"
    periodos_vol = 20  # Janela da Volatilidade Histórica
    print(f"    -> Rodando estratégia {nome_estrategia} (com Volatilidade) para {ativo}...")

    # 1. Mapear caminhos dos arquivos necessários (Preço, RSI e Volatilidade)
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_rsi = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_RSI_14.csv")
    arq_vol = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_VOLHIST_{periodos_vol}.csv")

    # Verificação de segurança de arquivos
    for arq in [arq_raw, arq_rsi, arq_vol]:
        if not os.path.exists(arq):
            print(f"       [Erro] Arquivo necessário não encontrado: {os.path.basename(arq)}")
            print("       Certifique-se de calcular os indicadores antes de rodar a estratégia.")
            return

    # 2. Carregar e unificar dados
    df = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_rsi = pd.read_csv(arq_rsi, parse_dates=True, index_col=0)
    df_vol = pd.read_csv(arq_vol, parse_dates=True, index_col=0)

    df["RSI_14"] = df_rsi["RSI_14"]
    df[f"Vol_Historica_{periodos_vol}"] = df_vol[f"Vol_Historica_{periodos_vol}"]

    # Limpar valores vazios decorrentes do aquecimento dos indicadores
    df = df.dropna()

    # 3. Lógica Quantitativa (Geração de Sinais de Extremos)
    df["Sinal"] = 0
    df.loc[df["RSI_14"] <= 20, "Sinal"] = 1   # COMPRA
    df.loc[df["RSI_14"] >= 80, "Sinal"] = -1  # VENDA

    # 4. Cálculo Dinâmico de Gain e Loss usando a Volatilidade Histórica
    # Como a Volatilidade Histórica no nosso arquivo está ANUALIZADA e em PERCENTUAL (ex: 30.0 para 30%):
    # Primeiro, trazemos ela de volta para a escala decimal diária aproximada:
    vol_diaria_decimal = (df[f"Vol_Historica_{periodos_vol}"] / 100) / np.sqrt(252)
    
    # Exemplo de Regra Dinâmica:
    # Definimos que o Stop Loss será equivalente a 1 variação diária média calculada em Reais (Preço * Vol Diária).
    # O Take Profit (Gain) será 2 vezes o valor do Stop Loss (proporção matemática de 2 para 1).
    df["Stop_Loss"] = round((df["Close"] * vol_diaria_decimal) * 2.0, 2)
    df["Take_Profit"] = round(df["Stop_Loss"] * 2.0, 2)

    # Evitar que em momentos de volatilidade nula o Stop fique zerado (mínimo de R$ 0.10, por exemplo)
    df["Stop_Loss"] = df["Stop_Loss"].clip(lower=0.10)
    df["Take_Profit"] = df["Take_Profit"].clip(lower=0.20)

    # 5. Filtrando colunas para exportação limpa
    df_saida = df[["Sinal", "Take_Profit", "Stop_Loss"]]

    # Salvar o arquivo de resultados na pasta de estratégias
    nome_saida = f"{ativo}_{tempo_grafico}_{nome_estrategia}.csv"
    caminho_saida = os.path.join(strategies_dir, nome_saida)
    df_saida.to_csv(caminho_saida)

    print(f"       Sinais e parâmetros dinâmicos de Volatilidade salvos em: {nome_saida}")