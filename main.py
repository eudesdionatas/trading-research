import os
import re
import pandas as pd

from src.indicators import rodar_todos_indicadores
from src.strategies import rodar_todas_estrategias

# Definindo caminhos globais (usando caminhos relativos robustos)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
CALC_DIR = os.path.join(BASE_DIR, "data", "calc")
INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
STRATEGIES_DIR = os.path.join(BASE_DIR, "data", "strategies")


def inicializar_diretorios():
    """Garante que a estrutura de pastas exista antes de rodar o pipeline."""
    for pasta in [RAW_DIR, CALC_DIR, INDICATORS_DIR, STRATEGIES_DIR]:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"Diretório criado: {pasta}")


def listar_arquivos_raw():
    """Varre a pasta data/raw buscando arquivos .csv no formato

    NOME-DO-ATIVO_TEMPO-GRÁFICO.csv
    """
    arquivos_validos = []

    if not os.path.exists(RAW_DIR):
        print(f"Erro: A pasta {RAW_DIR} não existe.")
        return arquivos_validos

    for arquivo in os.listdir(RAW_DIR):
        if arquivo.endswith(".csv"):
            # Expressão regular para validar o padrão ATIVO_TEMPO (ex: PETR4_D1)
            match = re.match(r"^([A-Z0-9]+)_([A-Z0-9]+)\.csv$", arquivo)
            if match:
                ativo, tempo_grafico = match.groups()
                arquivos_validos.append(
                    {
                        "nome_arquivo": arquivo,
                        "caminho_completo": os.path.join(RAW_DIR, arquivo),
                        "ativo": ativo,
                        "tempo_grafico": tempo_grafico,
                    }
                )
            else:
                print(f"Aviso: Arquivo '{arquivo}' ignorado por não seguir o padrão ATIVO_TEMPO.csv")

    return arquivos_validos


def processar_pipeline():
    """Função principal que orquestra os passos 1 e 2 do sistema."""
    inicializar_diretorios()

    print("\n[Passo 1] Varrendo arquivos em data/raw...")
    ativos_encontrados = listar_arquivos_raw()

    if not ativos_encontrados:
        print("Nenhum arquivo válido encontrado em data/raw para processamento.")
        return

    print(f"Total de ativos encontrados para processar: {len(ativos_encontrados)}")

    # Loop principal por ativo/tempo gráfico
    for item in ativos_encontrados:
        print(f"\n» Processando {item['ativo']} no tempo {item['tempo_grafico']}...")

        # Carrega o dado bruto
        df_raw = pd.read_csv(item["caminho_completo"], parse_dates=True, index_col=0)
        df_raw = df_raw.sort_index()

        # --- PARTE 1: CÁLCULO DE INDICADORES PENDENTES ---
        # TODO: Aqui plugar o módulo src.indicadores para calcular e salvar em data/calc
        print(f"  -> Verificando/Calculando indicadores para {item['ativo']}...")
        rodar_todos_indicadores(
            df_raw, item["ativo"], item["tempo_grafico"], INDICATORS_DIR
        )

        # --- PARTE 2: GERAÇÃO DE SINAIS E ESTRATÉGIAS ---
        # TODO: Aqui plugar o módulo src.estrategias para gerar sinais e salvar em data/strategies
        print(f"  -> Computando estratégias de trade para {item['ativo']}...")
        rodar_todas_estrategias(item["ativo"], item["tempo_grafico"], RAW_DIR, INDICATORS_DIR, STRATEGIES_DIR)

    print("\nPipeline finalizado com sucesso!")


if __name__ == "__main__":
    processar_pipeline()