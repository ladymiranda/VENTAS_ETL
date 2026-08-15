"""
etl_ventas_main.py

Orquestador del pipeline ETL de ventas (raíz del proyecto, mismo rol que
main.py antes). Extrae -> limpia -> valida -> enriquece -> guarda en output/.
"""

import duckdb

from config.config import RAW_DIR, PARQUET_PATH, DB_PATH
from modulos.etl_ventas import extraer_y_limpiar
from modulos.feature_engineering import enriquecer_features
from modulos.validacion import validate_dataframe
from utils.logging_utils import configurar_logging


CSV_PATH = RAW_DIR / "Base de datos de Ventas.csv"


def guardar_parquet(df, path):
    df.write_parquet(path)
    print("Parquet generado correctamente.")


def guardar_duckdb(df, path, table_name="ventas_raw"):
    conn = duckdb.connect(str(path))
    conn.register("ventas_temp", df)
    conn.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM ventas_temp
    """)
    conn.close()
    print(f"Tabla {table_name} creada correctamente.")


def main():
    configurar_logging()

    print("=" * 50)
    print("INICIO DEL PROCESO ETL")
    print("=" * 50)

    # ==========================
    # 1. EXTRAER + LIMPIAR
    # ==========================
    print("Extrayendo y transformando datos...")

    df = extraer_y_limpiar(CSV_PATH)

    print(f"Registros extraídos: {df.height}")

    # ==========================
    # 2. VALIDAR
    # ==========================
    print("Validando datos...")

    registros_antes = df.height
    df, resumen_rechazos = validate_dataframe(df)

    if resumen_rechazos:
        print("\nSe encontraron registros inválidos (eliminados del dataset):")
        for regla, cantidad in resumen_rechazos.items():
            print(f"  - {regla}: {cantidad} registros")

    print(f"Validación completa. Rechazados: {registros_antes - df.height} | Registros válidos: {df.height}")

    # ==========================
    # 3. FEATURE ENGINEERING
    # ==========================
    print("Generando features adicionales...")

    df = enriquecer_features(df)

    # ==========================
    # 4. GUARDAR (OUTPUT)
    # ==========================
    print("Guardando Parquet...")

    guardar_parquet(df, PARQUET_PATH)

    print("Guardando en DuckDB...")

    guardar_duckdb(df, DB_PATH)

    print("=" * 50)
    print("Proceso ETL finalizado correctamente.")
    print("=" * 50)


if __name__ == "__main__":
    main()
