import os
import numpy as np
import pandas as pd


def executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir):
    """
    Executa a estratégia de Reversão de Extremos com o Oscilador Estocástico.
    
    Regras de Entrada:
    - COMPRA (1):  %K > %D  E  ambas as linhas (%K e %D) <= 20 (Sobrevenda)
    - VENDA (-1):  %K < %D  E  ambas as linhas (%K e %D) >= 80 (Sobrecompra)
    
    Metas Financeiras Dinâmicas:
    - Baseadas na Volatilidade Histórica de 20 períodos do ativo.
    - Loss = Preço de Fechamento * Volatilidade Diária (Decimal).
    - Gain = 2 * Loss.
    """
    nome_estrategia = "STOCH_EXTREME_REVERSAL_14_3"
    periodos_stoch_k = 14
    suavizacao_stoch_d = 3
    periodos_vol = 20  # Janela da Volatilidade Histórica
    
    print(f"    -> Rodando estratégia {nome_estrategia} (com Volatilidade) para {ativo}...")

    # 1. Mapear caminhos dos arquivos necessários (Preço, Estocástico e Volatilidade)
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_stoch = os.path.join(
        indicators_dir, f"{ativo}_{tempo_grafico}_STOCH_{periodos_stoch_k}_{suavizacao_stoch_d}.csv"
    )
    arq_vol = os.path.join(indicators_dir, f"{ativo}_{tempo_grafico}_VOLHIST_{periodos_vol}.csv")

    # Verificação de segurança de arquivos
    for arq in [arq_raw, arq_stoch, arq_vol]:
        if not os.path.exists(arq):
            print(f"       [Erro] Arquivo necessário não encontrado: {os.path.basename(arq)}")
            print("       Certifique-se de calcular os indicadores antes de rodar a estratégia.")
            return

    # 2. Carregar e unificar dados
    df = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_stoch = pd.read_csv(arq_stoch, parse_dates=True, index_col=0)
    df_vol = pd.read_csv(arq_vol, parse_dates=True, index_col=0)

    df["Stoch_K"] = df_stoch["Stoch_K"]
    df["Stoch_D"] = df_stoch["Stoch_D"]
    df[f"Vol_Historica_{periodos_vol}"] = df_vol[f"Vol_Historica_{periodos_vol}"]

    # Limpar valores vazios decorrentes do aquecimento dos indicadores
    df = df.dropna()

    # 3. Lógica Quantitativa (Geração de Sinais de Cruzamento em Extremos)
    # Inicializa a coluna de sinais: 0 (Neutro), 1 (Compra), -1 (Venda)
    df["Sinal"] = 0

    # Condições de Compra:
    # 1. Média Lenta (%D) menor que a Linha Rápida (%K) -> %K > %D
    # 2. Ambas as linhas menores ou iguais a 20 -> (Stoch_K <= 20) & (Stoch_D <= 20)
    condicao_compra = (df["Stoch_K"] > df["Stoch_D"]) & (df["Stoch_K"] <= 20) & (df["Stoch_D"] <= 20)
    df.loc[condicao_compra, "Sinal"] = 1

    # Condições de Venda:
    # 1. Média Lenta (%D) maior que a Linha Rápida (%K) -> %K < %D
    # 2. Ambas as linhas maiores ou iguais a 80 -> (Stoch_K >= 80) & (Stoch_D >= 80)
    condicao_venda = (df["Stoch_K"] < df["Stoch_D"]) & (df["Stoch_K"] >= 80) & (df["Stoch_D"] >= 80)
    df.loc[condicao_venda, "Sinal"] = -1

    # 4. Cálculo Dinâmico de Gain e Loss usando a Volatilidade Histórica Anualizada
    # Traz a volatilidade anualizada de volta para a escala diária em formato decimal
    vol_diaria_decimal = (df[f"Vol_Historica_{periodos_vol}"] / 100) / np.sqrt(252)
    
    # Cálculo das barreiras de stop e ganho em Reais
    df["Stop_Loss"] = round(df["Close"] * vol_diaria_decimal, 2)
    df["Take_Profit"] = round(df["Stop_Loss"] * 2.0, 2)

    # Evita que em momentos atípicos de baixíssima volatilidade o Stop fique zerado
    df["Stop_Loss"] = df["Stop_Loss"].clip(lower=0.10)
    df["Take_Profit"] = df["Take_Profit"].clip(lower=0.20)

    # 5. Filtrando colunas para exportação limpa
    df_saida = df[["Sinal", "Take_Profit", "Stop_Loss"]]

    # Salvar o arquivo de resultados na pasta de estratégias
    nome_saida = f"{ativo}_{tempo_grafico}_{nome_estrategia}.csv"
    caminho_saida = os.path.join(strategies_dir, nome_saida)
    df_saida.to_csv(caminho_saida)

    print(f"       Sinais e alvos dinâmicos calculados salvos em: {nome_saida}")