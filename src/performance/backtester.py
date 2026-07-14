import os
import pandas as pd


def rodar_backtest(ativo, tempo_grafico, nome_estrategia, raw_dir, strategies_dir, multiplicador=1.0, contratos=1):
    """
    Simulador agnóstico: Lê os sinais de qualquer estratégia e cruza com os
    preços originais para calcular o lucro/prejuízo financeiro das operações.
    """
    arq_raw = os.path.join(raw_dir, f"{ativo}_{tempo_grafico}.csv")
    arq_estrategia = os.path.join(strategies_dir, f"{ativo}_{tempo_grafico}_{nome_estrategia}.csv")

    if not os.path.exists(arq_raw) or not os.path.exists(arq_estrategia):
        return pd.DataFrame()

    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    df_strat = pd.read_csv(arq_estrategia, parse_dates=True, index_col=0)

    # Remove qualquer coluna da estratégia que já exista no dado bruto
    colunas_conflitantes = df_strat.columns.intersection(df_raw.columns)
    df_strat = df_strat.drop(columns=colunas_conflitantes)

    df = df_raw.join(df_strat, how="left")

    tem_entrada_customizada = "Preco_Entrada" in df.columns
    tem_alvos = "Stop_Loss" in df.columns and "Take_Profit" in df.columns

    lista_trades = []
    posicionado = False
    trade_atual = {}

    for data, linha in df.iterrows():
        sinal = linha.get("Sinal", 0)

        # 1. MONITORAMENTO DE SAÍDA
        if posicionado:
            high = linha["High"]
            low = linha["Low"]
            fechamento = linha["Close"]
            
            atingiu_loss = False
            atingiu_gain = False
            sinal_inverso = False
            preco_saida = 0
            motivo_saida = ""

            if tem_alvos and pd.notna(trade_atual.get("Stop_Loss")):
                if trade_atual["Direcao"] == "COMPRA":
                    atingiu_loss = low <= trade_atual["Stop_Loss"]
                    atingiu_gain = high >= trade_atual["Take_Profit"]
                else:
                    atingiu_loss = high >= trade_atual["Stop_Loss"]
                    atingiu_gain = low <= trade_atual["Take_Profit"]
            else:
                if (trade_atual["Direcao"] == "COMPRA" and sinal == -1) or \
                   (trade_atual["Direcao"] == "VENDA" and sinal == 1):
                    sinal_inverso = True

            if atingiu_loss:
                motivo_saida = "Stop Loss"
                preco_saida = trade_atual["Stop_Loss"]
            elif atingiu_gain:
                motivo_saida = "Take Profit"
                preco_saida = trade_atual["Take_Profit"]
            elif sinal_inverso:
                motivo_saida = "Inversão de Sinal"
                preco_saida = fechamento

            if motivo_saida:
                # Calcula a variação bruta (Pontos no Índice/Dólar ou Centavos na Ação)
                if trade_atual["Direcao"] == "COMPRA":
                    pontos = preco_saida - trade_atual["Preco_Entrada"]
                else:
                    pontos = trade_atual["Preco_Entrada"] - preco_saida
                    
                # Converte os pontos em R$ usando o multiplicador e a quantidade de contratos
                lucro_financeiro = pontos * multiplicador * contratos
                
                # O retorno % se mantém puramente como variação do preço do ativo
                retorno_pct = (pontos / trade_atual["Preco_Entrada"]) * 100

                trade_atual.update({
                    "Data_Saida": data.date(),
                    "Preco_Saida": round(preco_saida, 2),
                    "Pontos_Capturados": round(pontos, 2),
                    "Resultado_R$": round(lucro_financeiro, 2),
                    "Retorno_%": round(retorno_pct, 2),
                    "Status": motivo_saida
                })
                
                lista_trades.append(trade_atual)
                posicionado = False
                trade_atual = {}
                continue 

        # 2. MONITORAMENTO DE ENTRADA
        if not posicionado and sinal in [1, -1]:
            direcao = "COMPRA" if sinal == 1 else "VENDA"
            
            if tem_entrada_customizada and pd.notna(linha["Preco_Entrada"]):
                preco_entrada = linha["Preco_Entrada"]
            else:
                preco_entrada = linha["Close"]

            if pd.isna(preco_entrada) or preco_entrada <= 0:
                continue

            trade_atual = {
                "Ativo": ativo,
                "Data_Entrada": data.date(),
                "Direcao": direcao,
                "Preco_Entrada": round(preco_entrada, 2),
                "Contratos": contratos
            }

            if tem_alvos:
                trade_atual["Stop_Loss"] = round(linha["Stop_Loss"], 2) if pd.notna(linha["Stop_Loss"]) else None
                trade_atual["Take_Profit"] = round(linha["Take_Profit"], 2) if pd.notna(linha["Take_Profit"]) else None

            posicionado = True

    return pd.DataFrame(lista_trades)