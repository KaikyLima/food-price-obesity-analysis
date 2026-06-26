import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


def comparar_modelos_regressao(X: pd.DataFrame, y: pd.Series, test_size: float = 0.25, random_state: int = 42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    modelos = {
        "Baseline (média)": DummyRegressor(strategy="mean"),
        "Regressão Linear":  LinearRegression(),
        "Random Forest":     RandomForestRegressor(n_estimators=300, max_depth=5, random_state=random_state),
        "XGBoost": XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.1, random_state=random_state)
    }

    resultados, treinados = [], {}
    for nome, modelo in modelos.items():
        if nome == "Regressão Linear":
            modelo.fit(X_train_sc, y_train)
            y_pred = modelo.predict(X_test_sc)
        else:
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)

        resultados.append({
            "Modelo": nome,
            "MAE":  mean_absolute_error(y_test, y_pred),
            "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
            "R2":   r2_score(y_test, y_pred),
        })
        treinados[nome] = modelo

    df_resultados = pd.DataFrame(resultados)

    info = {
        "modelos": treinados,
        "scaler": scaler,
        "split": (X_train, X_test, y_train, y_test),
    }

    return df_resultados, info


def extrair_coeficientes(modelo, feature_names) -> pd.Series:
    """Extrai coeficientes (Regressão Linear) ou importâncias de features (Modelos de Árvore)."""
    # 1. Verifica se é um modelo linear (Regressão Linear)
    if hasattr(modelo, 'coef_'):
        importancias = pd.Series(modelo.coef_, index=feature_names)
        # Ordena pelo valor absoluto para ver o impacto real, seja positivo ou negativo
        return importancias.reindex(importancias.abs().sort_values(ascending=False).index)

    # 2. Verifica se é um modelo baseado em árvores (Random Forest, XGBoost)
    elif hasattr(modelo, 'feature_importances_'):
        importancias = pd.Series(modelo.feature_importances_, index=feature_names)
        # Importâncias de árvores são sempre positivas, basta ordenar decrescente
        return importancias.sort_values(ascending=False)

    # 3. Tratamento de exceção para modelos como DummyRegressor que não possuem os atributos
    else:
        return pd.Series(0, index=feature_names)