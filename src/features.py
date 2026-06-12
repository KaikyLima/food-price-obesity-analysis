import pandas as pd

ORDEM_NUM = {
    "Less than $15,000"  : 1,
    "$15,000 - $24,999"  : 2,
    "$25,000 - $34,999"  : 3,
    "$35,000 - $49,999"  : 4,
    "$50,000 - $74,999" : 5,
    "$75,000 or greater" : 6,
}

REGIOES = {1: "Nordeste", 2: "Centro-Oeste", 3: "Sul", 4: "Oeste"}


def preparar_features_renda(df_analitico_renda: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:

    df = df_analitico_renda.copy()

    df["Income_Num"] = df["Income_Group"].map(ORDEM_NUM)


    income_centrado = df["Income_Num"] - df["Income_Num"].mean()
    price_centrado  = df["Price_Healthy"] - df["Price_Healthy"].mean()
    df["Renda_x_PriceHealthy"] = income_centrado * price_centrado

    regiao_dummies = pd.get_dummies(df["Metroregion_code"].map(REGIOES), prefix="Regiao", drop_first=True)

    X = pd.concat([
        df[["Income_Num", "Price_Healthy", "Price_Processed", "Price_Ratio", "Renda_x_PriceHealthy", "Year"]],
        regiao_dummies,
    ], axis=1)

    y = df["Obesity_Rate"]
    groups = df["State"]

    return X, y, groups