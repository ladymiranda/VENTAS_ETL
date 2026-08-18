import pandas as pd

ORDEN_MESES = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12,
}

def historial_por_cliente(df: pd.DataFrame) -> pd.DataFrame:

    historial = (
        df.groupby("Cliente_ID")
        .agg(
            total_compras=("Cliente_ID", "size"),
            unidades_totales=("Unidades_Vendidas", "sum"),
            monto_total=("Ingresos", "sum"),
            ticket_promedio=("Ingresos", "mean"),
            monto_max=("Ingresos", "max"),
        )
        .reset_index()
    )

    historial["monto_total"] = historial["monto_total"].round(2)
    historial["ticket_promedio"] = historial["ticket_promedio"].round(2)

    return df.merge(historial, on="Cliente_ID", how="left")


def recencia_por_cliente(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["Mes_Numero"] = df["Mes"].map(ORDEN_MESES)

    df["periodo"] = df["Año"] * 12 + df["Mes_Numero"]

    periodo_actual = df["periodo"].max()

    recencia = (
        df.groupby("Cliente_ID")["periodo"]
        .max()
        .reset_index(name="ultimo_periodo_compra")
    )

    recencia["meses_desde_ultima_compra"] = (
        periodo_actual - recencia["ultimo_periodo_compra"]
    )

    df = df.merge(recencia, on="Cliente_ID", how="left")

    df = df.drop(columns=["Mes_Numero"])

    return df


def participacion_por_producto(df: pd.DataFrame) -> pd.DataFrame:

    resumen = (
        df.groupby("Producto", as_index=False)["Ingresos"]
        .sum()
        .rename(columns={"Ingresos": "revenue_producto"})
    )

    revenue_total = resumen["revenue_producto"].sum()

    resumen["participacion_pct"] = (
        resumen["revenue_producto"] / revenue_total * 100
    ).round(2)

    resumen["ranking_producto"] = (
        resumen["revenue_producto"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    return df.merge(resumen, on="Producto", how="left")


def segmentar_clientes_por_valor(df: pd.DataFrame) -> pd.DataFrame:

    historial_unico = (
        df[["Cliente_ID", "monto_total"]]
        .drop_duplicates(subset="Cliente_ID")
        .copy()
    )

    historial_unico["segmento_valor"] = pd.qcut(
        historial_unico["monto_total"],
        q=4,
        labels=["Bajo", "Medio-bajo", "Medio-alto", "Alto"],
        duplicates="drop",
    )

    historial_unico["segmento_valor"] = (
        historial_unico["segmento_valor"].astype(str)
    )

    return df.merge(
        historial_unico[["Cliente_ID", "segmento_valor"]],
        on="Cliente_ID",
        how="left",
    )


def enriquecer_features(df: pd.DataFrame) -> pd.DataFrame:

    df = historial_por_cliente(df)
    df = recencia_por_cliente(df)
    df = participacion_por_producto(df)
    df = segmentar_clientes_por_valor(df)

    return df

print(">>> feature_engineering.py cargado")
