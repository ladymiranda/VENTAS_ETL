import logging

import pandas as pd
import pandera.pandas as pa

from modulos.schema import schema_ventas

logger = logging.getLogger("ventas.validacion")


def validate_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:

    shape_antes = len(df)

    try:
        df_pd_limpio = schema_ventas.validate(df, lazy=True)

        logger.info(
            f"[ventas] Validación completa. "
            f"Registros válidos: {len(df_pd_limpio)}"
        )

        return df_pd_limpio, {}

    except pa.errors.SchemaErrors as err:

        fallas = err.failure_cases

        resumen = (
            fallas.groupby("check")["index"]
            .nunique()
            .to_dict()
        )

        for check_name, cantidad in resumen.items():
            logger.warning(
                f"[ventas] {check_name}: "
                f"{cantidad} registros -> eliminados"
            )

        indices_invalidos = fallas["index"].dropna().unique()

        df_pd_limpio = (
            df.drop(index=indices_invalidos, errors="ignore")
            .reset_index(drop=True)
        )

        eliminados = shape_antes - len(df_pd_limpio)

        logger.info(
            f"[ventas] Validación completa. "
            f"Rechazados: {eliminados} | "
            f"Registros válidos: {len(df_pd_limpio)}"
        )

        return df_pd_limpio, resumen


print(">>> validacion.py cargado")