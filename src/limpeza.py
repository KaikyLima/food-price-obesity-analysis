import pandas as pd
import duckdb
from IPython.display import display


def limpar_cdc(con: duckdb.DuckDBPyConnection) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Limpeza e filtragem do CDC via SQL (Etapa 4)."""
    cdc_geral = con.execute("""
        SELECT
            YearStart    AS Year,
            LocationAbbr AS State,
            QuestionID,
            Data_Value   AS Obesity_Rate
        FROM cdc_raw
        WHERE
            Class                       = 'Obesity / Weight Status'
            AND StratificationCategory1 = 'Total'
            AND YearStart               BETWEEN 2012 AND 2018
            AND Data_Value              IS NOT NULL
            AND LocationAbbr            NOT IN ('US', 'PR', 'GU', 'VI')
        ORDER BY Year, State, QuestionID
    """).df()

    cdc_renda = con.execute("""
        SELECT
            YearStart       AS Year,
            LocationAbbr    AS State,
            QuestionID,
            Stratification1 AS Income_Group,
            Data_Value      AS Obesity_Rate
        FROM cdc_raw
        WHERE
            Class                       = 'Obesity / Weight Status'
            AND StratificationCategory1 = 'Income'
            AND QuestionID              = 'Q036'
            AND Stratification1         != 'Data not reported'
            AND YearStart               BETWEEN 2012 AND 2018
            AND Data_Value              IS NOT NULL
            AND LocationAbbr            NOT IN ('US', 'PR', 'GU', 'VI')
        ORDER BY Year, State, Income_Group
    """).df()

    con.register("cdc_geral", cdc_geral)
    con.register("cdc_renda", cdc_renda)

    print(f"cdc_geral → {cdc_geral.shape[0]:,} linhas x {cdc_geral.shape[1]} colunas")
    print(f"cdc_renda → {cdc_renda.shape[0]:,} linhas x {cdc_renda.shape[1]} colunas")
    display(cdc_geral.head(6))
    display(cdc_renda.head(6))

    return cdc_geral, cdc_renda


def filtrar_usda(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Classificação e filtragem do USDA via SQL (Etapa 6)."""
    df_usda = con.execute("SELECT COUNT(*) AS n FROM usda_raw").df()["n"][0]

    usda_filtrado = con.execute("""
        SELECT
            Year, Month, Metroregion_code, EFPG_code, Value,
            CASE
                WHEN EFPG_code IN (
                    10000, 10025, 10050, 10075,
                    20000, 20075, 21500, 21525, 21550, 21575,
                    23000, 23075, 24500, 24525, 24550, 24575,
                    26000, 26525, 26550, 26575, 27500, 27550, 27575,
                    29000, 29025, 29050, 29075,
                    30000, 30025, 30050, 30075, 30090,
                    35000, 35050, 35075,
                    43000, 43030, 43060,
                    50000, 50050, 51500, 51550,
                    53000, 53050, 54500, 54550,
                    57500, 59000
                ) THEN 'healthy'
                WHEN EFPG_code IN (
                    15000, 15025, 15050, 15075,
                    46050, 56000,
                    60000, 62500, 65000, 67500,
                    72000, 72020, 72040, 72050,
                    73000, 73010, 73020, 73030, 73040, 73050, 73060,
                    75050
                ) THEN 'processed'
                ELSE NULL
            END AS Food_Type
        FROM usda_raw
        WHERE
            Attribute        = 'Unit_value_mean_wtd'
            AND Metroregion_code IN (1, 2, 3, 4)
            AND Food_Type    IS NOT NULL
        ORDER BY Year, Metroregion_code, EFPG_code
    """).df()

    con.register("usda_filtrado", usda_filtrado)

    print(f"Linhas antes:  {df_usda:,}")
    print(f"Linhas depois: {len(usda_filtrado):,}")
    print("\nDistribuição por tipo:")
    display(con.execute("""
        SELECT Food_Type, COUNT(DISTINCT EFPG_code) AS qtd_codigos, COUNT(*) AS total_linhas
        FROM usda_filtrado GROUP BY Food_Type
    """).df())
    display(usda_filtrado.head(8))

    return usda_filtrado


def agregar_usda_anual(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Agregação mensal → anual do USDA (Etapa 7)."""
    usda_anual = con.execute("""
        SELECT
            Year,
            Metroregion_code,
            ROUND(AVG(CASE WHEN Food_Type = 'healthy'   THEN Value END), 6) AS Price_Healthy,
            ROUND(AVG(CASE WHEN Food_Type = 'processed' THEN Value END), 6) AS Price_Processed,
            ROUND(
                AVG(CASE WHEN Food_Type = 'healthy'   THEN Value END) /
                AVG(CASE WHEN Food_Type = 'processed' THEN Value END)
            , 6) AS Price_Ratio
        FROM usda_filtrado
        GROUP BY Year, Metroregion_code
        ORDER BY Year, Metroregion_code
    """).df()

    con.register("usda_anual", usda_anual)
    print(f"Shape: {usda_anual.shape}")
    display(usda_anual)

    return usda_anual


def criar_mapeamento_estados(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Tabela de mapeamento estado → região (Etapa 8)."""
    mapeamento = [
        *[(s, 1) for s in ["CT","ME","MA","NH","NJ","NY","PA","RI","VT"]],
        *[(s, 2) for s in ["IL","IN","IA","KS","MI","MN","MO","NE","ND","OH","SD","WI"]],
        *[(s, 3) for s in ["AL","AR","DE","DC","FL","GA","KY","LA","MD","MS","NC","OK","SC","TN","TX","VA","WV"]],
        *[(s, 4) for s in ["AK","AZ","CA","CO","HI","ID","MT","NV","NM","OR","UT","WA","WY"]],
    ]

    df_mapeamento = pd.DataFrame(mapeamento, columns=["State", "Metroregion_code"])
    con.register("state_region", df_mapeamento)

    print(f"Total de estados mapeados: {len(df_mapeamento)}")
    display(con.execute("""
        SELECT Metroregion_code, COUNT(*) AS estados
        FROM state_region GROUP BY Metroregion_code ORDER BY Metroregion_code
    """).df())

    print("\nEstados no CDC sem mapeamento (deve ser zero):")
    display(con.execute("""
        SELECT DISTINCT c.State FROM cdc_geral c
        LEFT JOIN state_region sr ON c.State = sr.State
        WHERE sr.State IS NULL
    """).df())

    return df_mapeamento


def criar_tabela_analitica(con: duckdb.DuckDBPyConnection) -> tuple[pd.DataFrame, pd.DataFrame]:
    """JOIN final — tabela analítica (Etapa 9)."""
    con.execute("""
        CREATE OR REPLACE TABLE analitico_precos AS
        SELECT
            c.Year, c.State, c.QuestionID, sr.Metroregion_code,
            ROUND(c.Obesity_Rate,    2) AS Obesity_Rate,
            ROUND(u.Price_Healthy,   6) AS Price_Healthy,
            ROUND(u.Price_Processed, 6) AS Price_Processed,
            ROUND(u.Price_Ratio,     6) AS Price_Ratio
        FROM      cdc_geral    c
        JOIN      state_region sr ON c.State = sr.State
        JOIN      usda_anual   u  ON c.Year  = u.Year
                                  AND sr.Metroregion_code = u.Metroregion_code
        ORDER BY  c.Year, c.State, c.QuestionID
    """)

    con.execute("""
        CREATE OR REPLACE TABLE analitico_renda AS
        SELECT
            c.Year, c.State, c.Income_Group, sr.Metroregion_code,
            ROUND(c.Obesity_Rate,    2) AS Obesity_Rate,
            ROUND(u.Price_Healthy,   6) AS Price_Healthy,
            ROUND(u.Price_Processed, 6) AS Price_Processed,
            ROUND(u.Price_Ratio,     6) AS Price_Ratio
        FROM      cdc_renda    c
        JOIN      state_region sr ON c.State = sr.State
        JOIN      usda_anual   u  ON c.Year  = u.Year
                                  AND sr.Metroregion_code = u.Metroregion_code
        ORDER BY  c.Year, c.State, c.Income_Group
    """)

    df_analitico_precos = con.execute("SELECT * FROM analitico_precos").df()
    df_analitico_renda  = con.execute("SELECT * FROM analitico_renda").df()

    print(f"analitico_precos → {df_analitico_precos.shape[0]:,} linhas x {df_analitico_precos.shape[1]} colunas")
    print(f"analitico_renda  → {df_analitico_renda.shape[0]:,} linhas x {df_analitico_renda.shape[1]} colunas")
    print("\nNulos em analitico_precos:", df_analitico_precos.isnull().sum().sum())
    print("Nulos em analitico_renda: ", df_analitico_renda.isnull().sum().sum())
    print("\nTabelas no DuckDB:")
    display(con.execute("SHOW TABLES").df())
    display(df_analitico_precos.head(6))
    display(df_analitico_renda.head(6))

    return df_analitico_precos, df_analitico_renda
