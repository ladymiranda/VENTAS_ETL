"""
modulos/validacion.py

Valida el DataFrame de ventas (Polars) contra modulos/schema.py usando Pandera.
Pandera trabaja sobre pandas, así que convertimos ida y vuelta: el pipeline
sigue en Polars, la validación es el único tramo en pandas.
"""

import logging

import polars as pl
import pandera.pandas as pa

from modulos.schema import schema_ventas

logger = logging.getLogger("ventas.validacion")


def validate_dataframe(df: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """
    Recibe un DataFrame de Polars, valida con Pandera y devuelve:
        df_limpio : Polars DataFrame solo con las filas válidas.
        resumen   : dict {regla: cantidad_rechazada} — vacío si todo pasó.
    """
    shape_antes = df.height
    df_pd = df.to_pandas()

    try:
        df_pd_limpio = schema_ventas.validate(df_pd, lazy=True)
        logger.info(f"[ventas] Validación completa. Registros válidos: {len(df_pd_limpio)}")
        return pl.from_pandas(df_pd_limpio), {}

    except pa.errors.SchemaErrors as err:
        fallas = err.failure_cases
        resumen = fallas.groupby("check")["index"].nunique().to_dict()

        for check_name, cantidad in resumen.items():
            logger.warning(f"[ventas] {check_name}: {cantidad} registros -> eliminados")

        indices_invalidos = fallas["index"].dropna().unique()
        df_pd_limpio = df_pd.drop(index=indices_invalidos, errors="ignore").reset_index(drop=True)

        eliminados = shape_antes - len(df_pd_limpio)
        logger.info(
            f"[ventas] Validación completa. Rechazados: {eliminados} | "
            f"Registros válidos: {len(df_pd_limpio)}"
        )

        return pl.from_pandas(df_pd_limpio), resumen


print(">>> validacion.py cargado")
