import os
import itertools
import pandas as pd

# Importando os módulos do nosso framework
from src.indicators import atr_fib_trend
from src.strategies import pullback_atr_fib
from src.performance.backtester import rodar_backtest

# Configurações de Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
STRATEGIES_DIR = os.path.join(BASE_DIR, "data", "strategies")


def otimizar_atr_fib(ativo, tempo_grafico, capital_inicial=10000.0):
    """
    Roda um Grid Search testando múltiplas combinações para a estratégia ATR Fib.
    """
    print("==================================================")
    print(f"   OTIMIZADOR QUANTITATIVO: {ativo} ({tempo_grafico})")
    print("==================================================\n")

    # 1. Definir a Matriz de Parâmetros (Grid)
    # Exemplo: Testaremos médias de 50 a 150 e ATRs de 50 a 150
    tipos_ma = ["SMMA"]
    periodos_ma = [50, 75, 100, 125, 150]
    periodos_atr = [50, 75, 100, 125, 150]
    
    # Gera todas as combinações possíveis
    combinacoes = list(itertools.product(tipos_ma, periodos_ma, periodos_atr))
    total_testes = len(combinacoes)
    
    print(f"Total de combinações a serem testadas: {total_testes}")
    print("Iniciando varredura... (Isso pode levar alguns segundos)\n")

    # Carrega o dado bruto uma única vez na memória para passar aos cálculos
    arq_raw = os.path.join(RAW_DIR, f"{ativo}_{tempo_grafico}.csv")
    if not os.path.exists(arq_raw):
        print(f"Erro: Arquivo bruto {arq_raw} não encontrado.")
        return
        
    df_raw = pd.read_csv(arq_raw, parse_dates=True, index_col=0)
    resultados_finais = []

    # 2. Loop Principal de Otimização
    for i, (ma_type, ma_len, atr_len) in enumerate(combinacoes, 1):
        nome_estrategia = f"PULLBACK_ATRFIB_{ma_type}{ma_len}_ATR{atr_len}"
        
        # A. Calcular o Indicador com os parâmetros atuais
        atr_fib_trend.calcular(
            df_raw, ativo, tempo_grafico, INDICATORS_DIR, 
            ma_type=ma_type, ma_len=ma_len, atr_len=atr_len, atr_mult=3.0
        )
        
        # B. Calcular a Estratégia (Sinais)
        pullback_atr_fib.executar(
            ativo, tempo_grafico, RAW_DIR, INDICATORS_DIR, STRATEGIES_DIR,
            ma_type=ma_type, ma_len=ma_len, atr_len=atr_len
        )
        
        # C. Rodar o Backtest Financeiro
        df_trades = rodar_backtest(ativo, tempo_grafico, nome_estrategia, RAW_DIR, STRATEGIES_DIR)
        
        # D. Extrair as Métricas
        if df_trades.empty:
            continue
            
        total_trades = len(df_trades)
        lucros = df_trades[df_trades["Retorno_%"] > 0]
        win_rate = (len(lucros) / total_trades) * 100
        
        # Cálculos com Capital (Juros Compostos)
        df_trades["Fator_Crescimento"] = 1 + (df_trades["Retorno_%"] / 100)
        df_trades["Capital_Acumulado"] = capital_inicial * df_trades["Fator_Crescimento"].cumprod()
        
        capital_final = df_trades["Capital_Acumulado"].iloc[-1]
        lucro_liquido = capital_final - capital_inicial
        retorno_pct = (lucro_liquido / capital_inicial) * 100
        
        # Drawdown
        df_trades["Pico_Capital"] = df_trades["Capital_Acumulado"].cummax()
        df_trades["Drawdown_R$"] = df_trades["Capital_Acumulado"] - df_trades["Pico_Capital"]
        df_trades["Drawdown_%"] = (df_trades["Drawdown_R$"] / df_trades["Pico_Capital"]) * 100
        drawdown_maximo = df_trades["Drawdown_%"].min()
        
        # Salva o resultado deste loop
        resultados_finais.append({
            "MA_Len": ma_len,
            "ATR_Len": atr_len,
            "Trades": total_trades,
            "WinRate(%)": round(win_rate, 2),
            "Retorno(%)": round(retorno_pct, 2),
            "Lucro_R$": round(lucro_liquido, 2),
            "Drawdown_Max(%)": round(drawdown_maximo, 2)
        })
        
        # Feedback visual de progresso simples
        if i % 5 == 0:
            print(f"Testados {i}/{total_testes}...")

    # 3. Ranqueamento dos Resultados
    if not resultados_finais:
        print("Nenhuma estratégia gerou operações válidas.")
        return

    df_ranking = pd.DataFrame(resultados_finais)
    
    # Ordenamos os resultados pelo maior Lucro Líquido
    df_ranking = df_ranking.sort_values(by="Lucro_R$", ascending=False).reset_index(drop=True)

    print("\n==================================================")
    print("                TOP 10 RESULTADOS                 ")
    print("==================================================")
    # Configuração do pandas para exibir todas as colunas no print sem quebrar linha
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print(df_ranking.head(10).to_string(index=False))
    print("==================================================\n")


if __name__ == "__main__":
    ativo_alvo = "PETR4"
    tempo_alvo = "D1"
    
    # Executa a varredura
    otimizar_atr_fib(ativo_alvo, tempo_alvo)