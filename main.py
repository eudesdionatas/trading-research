import yfinance as yf

dados = yf.download(
    "PETR4.SA",
    start="2020-01-01",
    end="2026-01-01",
    auto_adjust=True
)

print(dados.head())
print(dados.tail())
print("a")

dados.to_csv("data/raw/PETR4.csv")

print("Arquivo salvo com sucesso!")