import numpy as np
import pandas as pd
from scipy import stats
from IPython.display import display

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
    return "v significativo" if p < 0.05 else "x não significativo"


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


def tendencia_obesidade_por_renda(
    df_analitico_renda: pd.DataFrame,
    anos_projecao: int = 3,
    confianca: float = 0.95,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    media_por_grupo_ano = (
        df_analitico_renda
        .groupby(["Income_Group", "Year"])["Obesity_Rate"]
        .mean()
        .reset_index()
    )

    ultimo_ano = int(media_por_grupo_ano["Year"].max())
    primeiro_ano = int(media_por_grupo_ano["Year"].min())
    n_anos = ultimo_ano - primeiro_ano + 1

    print(f"Dados observados: {primeiro_ano}–{ultimo_ano} ({n_anos} anos)")
    print(f"Projetando {anos_projecao} ano(s) além de {ultimo_ano} "
          f"(intervalo de predição a {int(confianca * 100)}%)")
    if anos_projecao > n_anos:
        print("atenção: horizonte de projeção maior que o período observado — "
              "resultados puramente ilustrativos, discutir como limitação.")

    t_val = stats.t.ppf((1 + confianca) / 2, df=n_anos - 2)

    tendencias, previsoes = [], []
    for faixa in ORDEM_NUM:
        d = media_por_grupo_ano[media_por_grupo_ano["Income_Group"] == faixa]
        x, y = d["Year"].values, d["Obesity_Rate"].values

        slope, intercept, r, p, _ = stats.linregress(x, y)

        residuos = y - (intercept + slope * x)
        s = np.sqrt(np.sum(residuos ** 2) / (n_anos - 2))
        x_mean = x.mean()
        ss_x = np.sum((x - x_mean) ** 2)

        tendencias.append({"Income_Group": faixa, "slope": slope, "r": r, "p_valor": p})

        for ano in range(ultimo_ano + 1, ultimo_ano + 1 + anos_projecao):
            y0 = intercept + slope * ano
            se_pred = s * np.sqrt(1 + 1 / n_anos + (ano - x_mean) ** 2 / ss_x)
            margem = t_val * se_pred
            previsoes.append({
                "Income_Group": faixa, "Year": ano,
                "Obesity_Rate_previsto": y0,
                "limite_inferior": y0 - margem,
                "limite_superior": y0 + margem,
            })

    df_tendencias = pd.DataFrame(tendencias)
    df_previsoes = pd.DataFrame(previsoes)

    print("\nTendência por faixa de renda (Obesity_Rate ~ Year):")
    display(df_tendencias.round(4))

    print("\nProjeção (com intervalo de predição):")
    display(df_previsoes.round(2))

    return media_por_grupo_ano, df_tendencias, df_previsoes