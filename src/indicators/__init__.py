from . import exponential_moving_average 
from . import simple_moving_average
from . import rsi
from . import bollinger_bands
from . import macd
from . import trend_levels
from . import atr_fib_trend
from . import trend_filter_2pole
from . import support_resistance
from . import historical_volatility
from . import stochastic_oscillator

def rodar_todos_indicadores(df, ativo, tempo_grafico, calc_dir):
    """Executa a função de cálculo de cada módulo de indicador

    cadastrado no projeto.
    """
    # Exemplo: Rodando média móvel simples de 11 e de 40 conforme seus testes anteriores
    simple_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos=  7)
    simple_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 11)
    simple_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 17)
    simple_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 35)
    simple_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos=200)

    # Exemplo: Rodando média móvel exponencial de 7 e de 20 conforme seus testes anteriores
    exponential_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos=  7)
    exponential_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 11)
    exponential_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 17)
    exponential_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 35)
    exponential_moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 200)

    # 2. RSI Clássico de 14 períodos
    rsi.calcular(df, ativo, tempo_grafico, calc_dir, periodos=14)

    # 3. Bandas de Bollinger Padrão (20 períodos, 2 desvios)
    bollinger_bands.calcular(df, ativo, tempo_grafico, calc_dir, periodos=20, desvios=2)

    # 4. MACD Padrão de Mercado (12, 26, 9)
    macd.calcular(df, ativo, tempo_grafico, calc_dir, fast=12, slow=26, sinal=9)

    # 5. Trend Levels (30 períodos)
    trend_levels.calcular(df, ativo, tempo_grafico, calc_dir, periodos=30)

    # 6. ATR + Fibonacci Trend (100 períodos, multiplicador 3.0)
    atr_fib_trend.calcular(df, ativo, tempo_grafico, calc_dir, ma_type="SMMA", ma_len=100, atr_len=100, atr_mult=3.0)

    # 7. Trend Filter 2 Pole (20 períodos, damping 0.1, bands 1.0)
    trend_filter_2pole.calcular(df, ativo, tempo_grafico, calc_dir, length=20, damping=0.1, bands=1.0)

    # 8. Suporte e Resistência (20 períodos)
    support_resistance.calcular(df, ativo, tempo_grafico, calc_dir, periodos=20)

    # 9. Volatilidade Histórica (20 períodos, 252 dias úteis)
    historical_volatility.calcular(df, ativo, tempo_grafico, calc_dir, periodos=20)
    
    # 10. Oscilador Estocástico (14 períodos, suavização 3)
    stochastic_oscillator.calcular(df, ativo, tempo_grafico, calc_dir, periodos_k=14, suavizacao_d=3)
    
    # Conforme criar novos arquivos (ex: rsi.py), basta importá-los e chamá-los aqui