from src.ingest.extract import extract_csv
from src.ingest.validate import validate_dataframe
from src.ingest.load import save_duckdb, save_parquet

from src.transform.clean import clean_dataframe

from src.utils.config import RAW_DIR


CSV_PATH = RAW_DIR / "Base de datos de Ventas.csv"

PARQUET_PATH = RAW_DIR / "ventas.parquet"


def main():

    print("=" * 50)
    print("INICIO DEL PROCESO ETL")
    print("=" * 50)

    # ==========================
    # 1. EXTRAER
    # ==========================
    print("Extrayendo datos...")

    df = extract_csv(CSV_PATH)

    print(f"Registros extraídos: {df.height}")


    # ==========================
    # 2. TRANSFORMAR / LIMPIAR
    # ==========================
    print("Transformando datos...")

    df = clean_dataframe(df)


    # ==========================
    # 3. VALIDAR
    # ==========================
    print("Validando datos...")

    errores = validate_dataframe(df)

    if errores:

        print("\nSe encontraron errores:")

        for error in errores:
            print(error)

        return


    print("Validación correcta.")


    # ==========================
    # 4. LOAD
    # ==========================
    print("Guardando Parquet...")

    save_parquet(df, PARQUET_PATH)


    print("Guardando en DuckDB...")

    save_duckdb(df, "ventas_raw")


    print("=" * 50)
    print("Proceso ETL finalizado correctamente.")
    print("=" * 50)


if __name__ == "__main__":
    main()