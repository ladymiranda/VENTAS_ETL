import polars as pl


ORDEN_MESES = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12,
}


def historial_por_cliente(df: pl.DataFrame) -> pl.DataFrame:
    """Técnica 1: total de compras, unidades, monto total, ticket promedio y monto máximo por cliente."""
    historial = df.group_by("Cliente_ID").agg([
        pl.len().alias("total_compras"),
        pl.col("Unidades_Vendidas").sum().alias("unidades_totales"),
        pl.col("Ingresos").sum().round(2).alias("monto_total"),
        pl.col("Ingresos").mean().round(2).alias("ticket_promedio"),
        pl.col("Ingresos").max().alias("monto_max"),
    ])
    return df.join(historial, on="Cliente_ID", how="left")


def recencia_por_cliente(df: pl.DataFrame) -> pl.DataFrame:
    """Técnica 2: meses desde la última compra de cada cliente (no hay fecha exacta, solo Año/Mes)."""
    df = df.with_columns(
        (pl.col("Año") * 12 + pl.col("Mes").replace_strict(ORDEN_MESES, return_dtype=pl.Int64))
        .alias("periodo")
    )
    periodo_actual = df["periodo"].max()

    recencia = (
        df.group_by("Cliente_ID")
        .agg(pl.col("periodo").max().alias("ultimo_periodo_compra"))
        .with_columns((periodo_actual - pl.col("ultimo_periodo_compra")).alias("meses_desde_ultima_compra"))
    )
    return df.join(recencia, on="Cliente_ID", how="left")


def participacion_por_producto(df: pl.DataFrame) -> pl.DataFrame:
    """Técnica 3: cuánto pesa cada producto en el revenue total y su ranking."""
    resumen = df.group_by("Producto").agg(pl.col("Ingresos").sum().alias("revenue_producto"))
    revenue_total = resumen["revenue_producto"].sum()

    resumen = resumen.with_columns([
        (pl.col("revenue_producto") / revenue_total * 100).round(2).alias("participacion_pct"),
        pl.col("revenue_producto").rank(method="ordinal", descending=True).cast(pl.Int64).alias("ranking_producto"),
    ])
    return df.join(resumen, on="Producto", how="left")


def segmentar_clientes_por_valor(df: pl.DataFrame) -> pl.DataFrame:
    """Técnica 4 (bonus): cuartiles de valor por cliente (Bajo/Medio-bajo/Medio-alto/Alto)."""
    historial_unico = df.select(["Cliente_ID", "monto_total"]).unique(subset="Cliente_ID")

    historial_unico = historial_unico.with_columns(
        pl.col("monto_total")
        .qcut(4, labels=["Bajo", "Medio-bajo", "Medio-alto", "Alto"])
        .cast(pl.Utf8)  # evita guardar como categórico (rompe pd.read_parquet directo por dict-encoding)
        .alias("segmento_valor")
    )
    return df.join(historial_unico.select(["Cliente_ID", "segmento_valor"]), on="Cliente_ID", how="left")


def enriquecer_features(df: pl.DataFrame) -> pl.DataFrame:
    """Aplica las 4 técnicas en orden y devuelve el DataFrame enriquecido."""
    df = historial_por_cliente(df)
    df = recencia_por_cliente(df)
    df = participacion_por_producto(df)
    df = segmentar_clientes_por_valor(df)
    return df


print(">>> feature_engineering.py cargado")
