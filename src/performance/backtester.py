import os
import pandas as pd


def rodar_backtest(ativo, tempo_grafico, nome_estrategia, raw_dir, strategies_dir):
    """
    Simulador agnóstico: Lê os sinais de qualquer estratégia e cruza com os
    preços originais para calcular o lucro/prejuízo das operações.
    """
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_estrategia = os.path.join(strategies_dir, f"{ativo}_{tempo_grafico}_{nome_estrategia}.csv")

    if not os.path.exists(arq_raw) or not os.path.exists(arq_estrategia):
        return pd.DataFrame()  # Retorna vazio se faltar dados

    # Carrega dados
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_strat = pd.read_csv(arq_estrategia, parse_dates=True, index_col=0)

    # --- CORREÇÃO DO ERRO ---
    # Remove qualquer coluna da estratégia que já exista no dado bruto (ex: High, Low, Close)
    colunas_conflitantes = df_strat.columns.intersection(df_raw.columns)
    df_strat = df_strat.drop(columns=colunas_conflitantes)

    # Junta os preços originais com os sinais da estratégia sem colisões
    df = df_raw.join(df_strat, how="left")

    # Verifica se a estratégia fornece preços de entrada/alvos customizados
    tem_entrada_customizada = "Preco_Entrada" in df.columns
    tem_alvos = "Stop_Loss" in df.columns and "Take_Profit" in df.columns

    lista_trades = []
    posicionado = False
    trade_atual = {}

    for data, linha in df.iterrows():
        sinal = linha.get("Sinal", 0)

        # 1. MONITORAMENTO DE SAÍDA (Se já estiver posicionado)
        if posicionado:
            high = linha["High"]
            low = linha["Low"]
            fechamento = linha["Close"]
            
            atingiu_loss = False
            atingiu_gain = False
            sinal_inverso = False
            preco_saida = 0
            motivo_saida = ""

            # Condição de Saída A: Por Stop Loss / Take Profit (Se a estratégia tiver)
            if tem_alvos and pd.notna(trade_atual.get("Stop_Loss")):
                if trade_atual["Direcao"] == "COMPRA":
                    atingiu_loss = low <= trade_atual["Stop_Loss"]
                    atingiu_gain = high >= trade_atual["Take_Profit"]
                else: # VENDA
                    atingiu_loss = high >= trade_atual["Stop_Loss"]
                    atingiu_gain = low <= trade_atual["Take_Profit"]

            # Condição de Saída B: Inversão de Sinal (Para estratégias de médias móveis, por ex)
            else:
                if (trade_atual["Direcao"] == "COMPRA" and sinal == -1) or \
                   (trade_atual["Direcao"] == "VENDA" and sinal == 1):
                    sinal_inverso = True

            # Processando a Saída
            if atingiu_loss:
                motivo_saida = "Stop Loss"
                preco_saida = trade_atual["Stop_Loss"]
            elif atingiu_gain:
                motivo_saida = "Take Profit"
                preco_saida = trade_atual["Take_Profit"]
            elif sinal_inverso:
                motivo_saida = "Inversão de Sinal"
                preco_saida = fechamento # Sai no fechamento do dia da inversão

            # Se alguma condição de saída foi disparada, consolida a operação
            if motivo_saida:
                if trade_atual["Direcao"] == "COMPRA":
                    lucro = preco_saida - trade_atual["Preco_Entrada"]
                else:
                    lucro = trade_atual["Preco_Entrada"] - preco_saida
                    
                retorno_pct = (lucro / trade_atual["Preco_Entrada"]) * 100

                trade_atual.update({
                    "Data_Saida": data.date(),
                    "Preco_Saida": round(preco_saida, 2),
                    "Resultado_R$": round(lucro, 2),
                    "Retorno_%": round(retorno_pct, 2),
                    "Status": motivo_saida
                })
                
                lista_trades.append(trade_atual)
                posicionado = False
                trade_atual = {}
                
                # Se saiu por inversão, o próprio candle de saída não servirá de entrada.
                # A nova entrada se dará no próximo sinal.
                continue 

        # 2. MONITORAMENTO DE ENTRADA (Se não estiver posicionado)
        if not posicionado and sinal in [1, -1]:
            direcao = "COMPRA" if sinal == 1 else "VENDA"
            
            # Define o preço de entrada (usa o da estratégia ou o fechamento do dia)
            if tem_entrada_customizada and pd.notna(linha["Preco_Entrada"]):
                preco_entrada = linha["Preco_Entrada"]
            else:
                preco_entrada = linha["Close"]

            # Proteção: Ignora sinais erráticos sem preço válido
            if pd.isna(preco_entrada) or preco_entrada <= 0:
                continue

            trade_atual = {
                "Ativo": ativo,
                "Data_Entrada": data.date(),
                "Direcao": direcao,
                "Preco_Entrada": round(preco_entrada, 2),
            }

            if tem_alvos:
                trade_atual["Stop_Loss"] = round(linha["Stop_Loss"], 2) if pd.notna(linha["Stop_Loss"]) else None
                trade_atual["Take_Profit"] = round(linha["Take_Profit"], 2) if pd.notna(linha["Take_Profit"]) else None

            posicionado = True

    return pd.DataFrame(lista_trades)