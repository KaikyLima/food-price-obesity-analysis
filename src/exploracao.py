import duckdb
from IPython.display import display


def explorar_cdc(con: duckdb.DuckDBPyConnection) -> None:
    """Exploração do CDC via SQL (Etapa 3)."""
    print("1. Valores de Class:")
    display(con.execute("SELECT DISTINCT Class FROM cdc_raw ORDER BY Class").df())

    print("2. Valores de StratificationCategory1:")
    display(con.execute("""
        SELECT DISTINCT StratificationCategory1, COUNT(*) AS n
        FROM cdc_raw GROUP BY StratificationCategory1 ORDER BY n DESC
    """).df())

    print("3. QuestionIDs dentro de 'Obesity / Weight Status':")
    display(con.execute("""
        SELECT DISTINCT QuestionID, Question
        FROM cdc_raw
        WHERE Class = 'Obesity / Weight Status'
        ORDER BY QuestionID
    """).df())

    print("4. Stratification1 quando categoria = 'Income':")
    display(con.execute("""
        SELECT DISTINCT Stratification1, COUNT(*) AS n
        FROM cdc_raw
        WHERE StratificationCategory1 = 'Income'
        GROUP BY Stratification1 ORDER BY Stratification1
    """).df())

    print("5. Anos disponíveis:")
    display(con.execute("SELECT DISTINCT YearStart FROM cdc_raw ORDER BY YearStart").df())

    print("6. Localizações que serão excluídas:")
    display(con.execute("""
        SELECT DISTINCT LocationAbbr FROM cdc_raw
        WHERE LocationAbbr IN ('US', 'PR', 'GU', 'VI')
    """).df())


def explorar_usda(con: duckdb.DuckDBPyConnection) -> None:
    """Exploração do USDA via SQL (Etapa 5)."""
    import pandas as pd

    print("1. Colunas e amostra:")
    display(con.execute("SELECT * FROM usda_raw LIMIT 3").df())

    print("\n2. Atributos disponíveis:")
    display(con.execute("""
        SELECT DISTINCT Attribute, COUNT(*) AS n
        FROM usda_raw GROUP BY Attribute ORDER BY n DESC
    """).df())

    print("\n3. Anos disponíveis:")
    display(con.execute("SELECT DISTINCT Year FROM usda_raw ORDER BY Year").df())

    print("\n4. Regiões disponíveis:")
    display(con.execute("""
        SELECT DISTINCT Metroregion_code, COUNT(*) AS n
        FROM usda_raw GROUP BY Metroregion_code ORDER BY Metroregion_code
    """).df())

    print("\n5. Códigos de alimento (EFPG_code):")
    display(con.execute("""
        SELECT MIN(EFPG_code) AS codigo_min, MAX(EFPG_code) AS codigo_max,
               COUNT(DISTINCT EFPG_code) AS total
        FROM usda_raw
    """).df())

    pd.set_option("display.max_rows", 100)
    print("\nTodos os EFPG_codes:")
    display(con.execute("SELECT DISTINCT EFPG_code FROM usda_raw ORDER BY EFPG_code").df())
