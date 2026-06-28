from . import moving_average
from . import rsi
from . import bollinger
from . import macd

def rodar_todos_indicadores(df, ativo, tempo_grafico, calc_dir):
    """Executa a função de cálculo de cada módulo de indicador

    cadastrado no projeto.
    """
    # Exemplo: Rodando média de 11 e de 40 conforme seus testes anteriores
    moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos=  7)
    moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 11)
    moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 17)
    moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos= 35)
    moving_average.calcular(df, ativo, tempo_grafico, calc_dir, periodos=200)

    # 2. RSI Clássico de 14 períodos
    rsi.calcular(df, ativo, tempo_grafico, calc_dir, periodos=14)

    # 3. Bandas de Bollinger Padrão (20 períodos, 2 desvios)
    bollinger.calcular(df, ativo, tempo_grafico, calc_dir, periodos=20, desvios=2)

    # 4. MACD Padrão de Mercado (12, 26, 9)
    macd.calcular(df, ativo, tempo_grafico, calc_dir, fast=12, slow=26, sinal=9)

    # Conforme criar novos arquivos (ex: rsi.py), basta importá-los e chamá-los aqui