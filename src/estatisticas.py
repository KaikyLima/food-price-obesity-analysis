import pandas as pd
from scipy import stats

REGIOES = {1: "Nordeste", 2: "Centro-Oeste", 3: "Sul", 4: "Oeste"}

ORDEM_NUM = {
    "Less than $15,000"  : 1,
    "$15,000 - $24,999"  : 2,
    "$25,000 - $34,999"  : 3,
    "$35,000 - $49,999"  : 4,
    "$50,000 - $74,999"  : 5,
    "$75,000 or greater" : 6,
}


def _sig(p: float) -> str:
    return "✓ significativo" if p < 0.05 else "✗ não significativo"


def correlacoes_preco_obesidade(df_obesidade: pd.DataFrame) -> None:
    """Correlações Price_Ratio e Price_Healthy × Obesity_Rate por região (H1)."""
    for label, col in [("Price_Ratio", "Price_Ratio"), ("Price_Healthy", "Price_Healthy")]:
        print("=" * 55)
        print(f"CORRELAÇÕES: {col} × Obesity_Rate por região")
        print("=" * 55)
        for codigo, nome in REGIOES.items():
            dados = df_obesidade[df_obesidade["Metroregion_code"] == codigo]
            r, p = stats.pearsonr(dados[col], dados["Obesity_Rate"])
            print(f"{nome:15} → r = {r:+.3f}  |  p = {p:.4f}  |  {_sig(p)}")
        print()


def correlacao_renda_obesidade(df_analitico_renda: pd.DataFrame) -> None:
    """Correlação Renda × Obesidade (H3)."""
    print("=" * 55)
    print("CORRELAÇÃO GERAL: Renda × Obesidade (H3)")
    print("=" * 55)

    df = df_analitico_renda.copy()
    df["Income_Num"] = df["Income_Group"].map(ORDEM_NUM)
    r, p = stats.pearsonr(df["Income_Num"], df["Obesity_Rate"])
    print(f"Renda (ordinal) × Obesidade → r = {r:+.3f}  |  p = {p:.4f}  |  {_sig(p)}")
