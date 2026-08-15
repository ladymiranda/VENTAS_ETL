print(">>> extract.py cargado")

import polars as pl


def extract_csv(file_path):
    print(">>> Entró a extract_csv")

    df = pl.read_csv(file_path)

    return df