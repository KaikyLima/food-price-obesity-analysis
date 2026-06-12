import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid")
os.makedirs("data/graficos", exist_ok=True)

REGIOES = {1: "Nordeste", 2: "Centro-Oeste", 3: "Sul", 4: "Oeste"}
CORES   = {1: "#e63946",  2: "#457b9d",      3: "#2a9d8f", 4: "#e9c46a"}

ORDEM_RENDA = [
    "Less than $15,000", "$15,000 - $24,999", "$25,000 - $34,999",
    "$35,000 - $49,999", "$50,000 - $74,999", "$75,000 or greater",
]
LABELS_RENDA = ["< \\$15k", "\\$15k–\\$25k", "\\$25k–\\$35k", "\\$35k–\\$50k", "\\$50k–\\$75k", "> \\$75k"]
CORES_RENDA  = {
    "Less than $15,000"  : "#e63946",
    "$15,000 - $24,999"  : "#e07b54",
    "$25,000 - $34,999"  : "#e9c46a",
    "$35,000 - $49,999"  : "#8ab17d",
    "$50,000 - $74,999"  : "#457b9d",
    "$75,000 or greater" : "#2a9d8f",
}
LABELS_RENDA_MAP = dict(zip(ORDEM_RENDA, LABELS_RENDA))


def grafico_evolucao_precos_obesidade(df_obesidade: pd.DataFrame) -> None:
    """Gráfico 1 — Evolução anual: preços e obesidade por região (H1)."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 14))

    for ax, col, titulo in zip(axes,
        ["Price_Healthy", "Price_Processed", "Obesity_Rate"],
        [
            "Evolução do Preço Médio de Alimentos Saudáveis por Região ($/100g)",
            "Evolução do Preço Médio de Alimentos Processados por Região ($/100g)",
            "Evolução da Taxa de Obesidade por Região (%)",
        ]
    ):
        for codigo, nome in REGIOES.items():
            dados = df_obesidade[df_obesidade["Metroregion_code"] == codigo].groupby("Year")[col].mean()
            ax.plot(dados.index, dados.values, marker="o", label=nome, color=CORES[codigo])
        ax.set_title(titulo)
        ax.set_ylabel("Preço ($/100g)" if "Price" in col else "Obesidade (%)")
        ax.legend()

    plt.tight_layout()
    path = "data/graficos/fig1_evolucao_precos_obesidade.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Salvo: {path}")


def grafico_correlacao_ratio_obesidade(df_obesidade: pd.DataFrame) -> None:
    """Gráfico 2 — Correlação Price_Ratio × Obesity_Rate por região (H1)."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for i, (codigo, nome) in enumerate(REGIOES.items()):
        dados = df_obesidade[df_obesidade["Metroregion_code"] == codigo]
        ax = axes[i]
        ax.scatter(dados["Price_Ratio"], dados["Obesity_Rate"],
                   color=CORES[codigo], alpha=0.7, edgecolors="white", s=60)
        z = np.polyfit(dados["Price_Ratio"], dados["Obesity_Rate"], 1)
        x_line = sorted(dados["Price_Ratio"])
        ax.plot(x_line, np.poly1d(z)(x_line), "--", color="gray", linewidth=1.5)
        corr = dados["Price_Ratio"].corr(dados["Obesity_Rate"])
        ax.set_title(f"{nome}  (r = {corr:.3f})")
        ax.set_xlabel("Price Ratio (saudável / processado)")
        ax.set_ylabel("Taxa de Obesidade (%)")

    plt.suptitle("Correlação entre Price Ratio e Obesidade por Região", fontsize=14, y=1.01)
    plt.tight_layout()
    path = "data/graficos/fig2_correlacao_ratio_obesidade.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Salvo: {path}")


def grafico_obesidade_por_renda(df_analitico_renda: pd.DataFrame) -> None:
    """Gráfico 3 — Obesidade por faixa de renda (H3)."""
    media_renda = (df_analitico_renda
                   .groupby("Income_Group")["Obesity_Rate"]
                   .mean()
                   .reindex(ORDEM_RENDA))

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(ORDEM_RENDA)), media_renda.values,
                  color=list(CORES_RENDA.values()))
    ax.set_xticks(range(len(ORDEM_RENDA)))
    ax.set_xticklabels(LABELS_RENDA)
    ax.set_ylabel("Taxa Média de Obesidade (%)")
    ax.set_title("Taxa Média de Obesidade por Faixa de Renda — 2012 a 2018 (H3)")
    for bar, val in zip(bars, media_renda.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    path = "data/graficos/fig3_obesidade_por_renda.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Salvo: {path}")


def grafico_evolucao_obesidade_renda(df_analitico_renda: pd.DataFrame) -> None:
    """Gráfico 4 — Evolução da obesidade por faixa de renda (H3)."""
    fig, ax = plt.subplots(figsize=(12, 6))

    for faixa, cor in CORES_RENDA.items():
        dados = (df_analitico_renda[df_analitico_renda["Income_Group"] == faixa]
                 .groupby("Year")["Obesity_Rate"].mean())
        ax.plot(dados.index, dados.values, marker="o",
                label=LABELS_RENDA_MAP[faixa], color=cor, linewidth=2)

    ax.set_title("Evolução da Obesidade por Faixa de Renda — 2012 a 2018 (H3)")
    ax.set_ylabel("Taxa Média de Obesidade (%)")
    ax.set_xlabel("Ano")
    ax.legend(title="Faixa de Renda", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    path = "data/graficos/fig4_evolucao_obesidade_renda.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Salvo: {path}")


def grafico_projecao_obesidade_renda(media_por_grupo_ano: pd.DataFrame, df_previsoes: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))
    ultimo_ano = media_por_grupo_ano["Year"].max()

    for faixa, cor in CORES_RENDA.items():
        hist = media_por_grupo_ano[media_por_grupo_ano["Income_Group"] == faixa]
        ax.plot(hist["Year"], hist["Obesity_Rate"], marker="o", color=cor, linewidth=2,
                label=LABELS_RENDA_MAP[faixa])

        prev = df_previsoes[df_previsoes["Income_Group"] == faixa]
        if prev.empty:
            continue

        ultimo_hist = hist.iloc[[-1]][["Year", "Obesity_Rate"]].rename(columns={"Obesity_Rate": "Obesity_Rate_previsto"})
        linha_prev = pd.concat([ultimo_hist, prev[["Year", "Obesity_Rate_previsto"]]])
        ax.plot(linha_prev["Year"], linha_prev["Obesity_Rate_previsto"], "--", color=cor, linewidth=2, alpha=0.8)

        ax.fill_between(prev["Year"], prev["limite_inferior"], prev["limite_superior"], color=cor, alpha=0.15)

    ax.axvline(ultimo_ano, color="gray", linestyle=":", linewidth=1)
    ax.set_title("Obesidade por Faixa de Renda — Histórico e Projeção com Intervalo de Predição (H3)")
    ax.set_ylabel("Taxa de Obesidade (%)")
    ax.set_xlabel("Ano")
    ax.legend(title="Faixa de Renda", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    path = "data/graficos/fig5_projecao_obesidade_renda.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Salvo: {path}")


def grafico_predito_vs_real(y_test: pd.Series, predicoes: dict, titulo: str, nome_arquivo: str) -> None:
    from sklearn.metrics import r2_score

    nomes = list(predicoes.keys())
    fig, axes = plt.subplots(1, len(nomes), figsize=(5 * len(nomes), 5), sharex=True, sharey=True)
    if len(nomes) == 1:
        axes = [axes]

    lim_min = min(y_test.min(), min(p.min() for p in predicoes.values())) - 1
    lim_max = max(y_test.max(), max(p.max() for p in predicoes.values())) + 1

    for ax, nome in zip(axes, nomes):
        y_pred = predicoes[nome]
        ax.scatter(y_test, y_pred, alpha=0.6, edgecolors="white", s=50, color="#457b9d")
        ax.plot([lim_min, lim_max], [lim_min, lim_max], "--", color="gray", linewidth=1.5)
        r2 = r2_score(y_test, y_pred)
        ax.set_title(f"{nome}  (R² = {r2:.3f})")
        ax.set_xlabel("Obesity_Rate real (%)")
        ax.set_ylabel("Obesity_Rate previsto (%)")
        ax.set_xlim(lim_min, lim_max)
        ax.set_ylim(lim_min, lim_max)

    plt.suptitle(titulo, fontsize=14, y=1.03)
    plt.tight_layout()
    path = f"data/graficos/{nome_arquivo}"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Salvo: {path}")


def grafico_coeficientes_regressao(coefs: pd.Series, titulo: str, nome_arquivo: str) -> None:
    coefs_ordenado = coefs.iloc[::-1]
    cores = ["#2a9d8f" if v >= 0 else "#e63946" for v in coefs_ordenado.values]

    fig, ax = plt.subplots(figsize=(8, max(3, 0.45 * len(coefs_ordenado))))
    ax.barh(coefs_ordenado.index, coefs_ordenado.values, color=cores)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Coeficiente padronizado")
    ax.set_title(titulo)
    plt.tight_layout()
    path = f"data/graficos/{nome_arquivo}"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Salvo: {path}")