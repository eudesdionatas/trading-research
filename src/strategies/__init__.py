from . import mooving_average_11_35_crossover_filtered_by_rsi


def rodar_todas_estrategias(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir):
    """Orquestra a execução de todas as estratégias de trading registradas."""
    # Executa a nossa primeira estratégia modular
    mooving_average_11_35_crossover_filtered_by_rsi.executar(ativo, tempo_grafico, raw_dir, indicators_dir, strategies_dir)

    # Futuras estratégias (ex: rsi_puro, bollinger_breakout) serão plugadas aqui