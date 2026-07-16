from . import ema_11_35_crossover_filtered_by_rsi
from . import pullback_atr_fib
from . import rsi_extreme_reversal
from . import stochastic_extreme_reversal



def rodar_todas_estrategias(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir):
    """Orquestra a execução de todas as estratégias de trading registradas."""
    # Executa a nossa primeira estratégia modular
    ema_11_35_crossover_filtered_by_rsi.executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir)

    # Executa a estratégia de pullback com ATR e Fibonacci
    pullback_atr_fib.executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir)

    # Executa a estratégia de Reversão de Extremos do RSI
    rsi_extreme_reversal.executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir)

    # Executa a estratégia de Reversão de Extremos com o Oscilador Estocástico
    stochastic_extreme_reversal.executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir)
    # Futuras estratégias (ex: rsi_puro, bollinger_breakout) serão plugadas aqui