import pandas as pd
import duckdb
import requests
import zipfile
import io
import os


def carregar_dados(con: duckdb.DuckDBPyConnection) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Baixa (ou carrega do disco) os dados CDC e USDA e registra no DuckDB."""
    os.makedirs("data", exist_ok=True)

    # ── CDC ──────────────────────────────────────────────────────────────────
    cdc_path = "data/cdc_dados.csv"
    if os.path.exists(cdc_path):
        print("CDC já baixado, carregando do disco...")
        df_cdc = pd.read_csv(cdc_path, low_memory=False)
    else:
        print("Baixando CDC...")
        url_cdc = "https://data.cdc.gov/api/views/hn4x-zwk7/rows.csv?accessType=DOWNLOAD"
        r = requests.get(url_cdc)
        df_cdc = pd.read_csv(io.BytesIO(r.content), low_memory=False)
        df_cdc.to_csv(cdc_path, index=False)
        print("Salvo em data/cdc_dados.csv")
    print(f"CDC  → {df_cdc.shape[0]:,} linhas x {df_cdc.shape[1]} colunas")

    # ── USDA ─────────────────────────────────────────────────────────────────
    usda_path   = "data/FMAP-Data.csv"
    readme_path = "data/FMAP-ReadMe.txt"
    if os.path.exists(usda_path):
        print("\nUSDA já baixado, carregando do disco...")
        df_usda = pd.read_csv(usda_path)
    else:
        print("\nBaixando USDA...")
        url_usda = "https://www.ers.usda.gov/media/5400/food-at-home-monthly-area-prices-2012-to-2018.zip?v=24363"
        r = requests.get(url_usda)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            print(f"Arquivos no ZIP: {z.namelist()}")
            csv_name = [f for f in z.namelist() if f.endswith(".csv")][0]
            with z.open(csv_name) as f:
                df_usda = pd.read_csv(f)
            df_usda.to_csv(usda_path, index=False)
            txt_name = [f for f in z.namelist() if f.endswith(".txt")][0]
            with z.open(txt_name) as f:
                readme_content = f.read()
            with open(readme_path, "wb") as f:
                f.write(readme_content)
            print("Salvo em data/FMAP-Data.csv e data/FMAP-ReadMe.txt")
    print(f"USDA → {df_usda.shape[0]:,} linhas x {df_usda.shape[1]} colunas")
    print(f"\nArquivos em data/: {os.listdir('data')}")

    # ── Registrar no DuckDB ───────────────────────────────────────────────────
    con.register("cdc_raw",  df_cdc)
    con.register("usda_raw", df_usda)
    print("\nTabelas disponíveis no DuckDB:")
    print(con.execute("SHOW TABLES").df())

    return df_cdc, df_usda
