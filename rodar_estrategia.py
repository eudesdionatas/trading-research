import os
# Este script é usado para rodar a estratégia ______________ isoladamente, sem precisar rodar todo o pipeline.
from src.strategies import rsi_atr_extreme_reversal

# Configura as pastas exatamente como no main
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
STRATEGIES_DIR = os.path.join(BASE_DIR, "data", "strategies")

# Altere aqui o ativo e tempo que quer testar isoladamente
ATIVO = "PETR4"
TEMPO = "D1"

print(f"Atualizando apenas os sinais de {ATIVO}...")
rsi_atr_extreme_reversal.executar(ATIVO, TEMPO, RAW_DIR, INDICATORS_DIR, STRATEGIES_DIR)
print("CSV de sinais atualizado com sucesso!")