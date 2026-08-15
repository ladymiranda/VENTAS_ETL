import polars as pl


def clean_dataframe(df):

    # ==========================
    # LIMPIAR CUSTOMER
    # ==========================

    df = df.with_columns(
        pl.col("Customer")
        .str.extract(r"(\d+)")
        .cast(pl.Int64)
        .alias("Cliente_ID")
    )


    # ==========================
    # TRANSFORMAR PRODUCTOS
    # ==========================

    productos = {
        "Product A": "Laptop",
        "Product B": "Smartphone",
        "Product C": "Tablet",
        "Product D": "Monitor",
        "Product E": "Teclado"
    }


    df = df.with_columns(
        pl.col("Product")
        .replace(productos)
        .alias("Producto")
    )


    # ==========================
    # TRANSFORMAR MESES
    # ==========================

    meses = {
        "Jan": "Enero",
        "Feb": "Febrero",
        "Mar": "Marzo",
        "Apr": "Abril",
        "May": "Mayo",
        "Jun": "Junio",
        "Jul": "Julio",
        "Aug": "Agosto",
        "Sep": "Septiembre",
        "Oct": "Octubre",
        "Nov": "Noviembre",
        "Dec": "Diciembre"
    }


    df = df.with_columns(
        pl.col("Month")
        .replace(meses)
        .alias("Mes")
    )


    # ==========================
    # RENOMBRAR COLUMNAS
    # ==========================

    df = df.rename(
        {
            "Year": "Año",
            "Units_Sold": "Unidades_Vendidas",
            "Price_per_Unit": "Precio_Unitario",
            "Revenue": "Ingresos",
            "Customer_Name": "Nombre_Cliente"
        }
    )


    # ==========================
    # NORMALIZAR DECIMALES
    # ==========================

    df = df.with_columns(
        [
            pl.col("Precio_Unitario")
            .round(2),

            pl.col("Ingresos")
            .round(2)
        ]
    )


    # ==========================
    # ELIMINAR COLUMNAS ANTIGUAS
    # ==========================

    df = df.drop(
        [
            "Customer",
            "Product",
            "Month"
        ],
        strict=False
    )


    return df