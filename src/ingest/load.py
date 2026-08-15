import duckdb
import polars as pl

from src.utils.config import DB_PATH


def save_parquet(df: pl.DataFrame, output_file):

    df.write_parquet(output_file)

    print("Parquet generado correctamente.")


def save_duckdb(df: pl.DataFrame, table_name):

    conn = duckdb.connect(DB_PATH)

    conn.register("ventas_temp", df)

    conn.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM ventas_temp
    """)

    conn.close()

    print(f"Tabla {table_name} creada correctamente.")