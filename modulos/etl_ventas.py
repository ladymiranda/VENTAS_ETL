import pandas as pd


def extract_csv(file_path):
    print(">>> Entró a extract_csv")
    df = pd.read_csv(file_path)
    return df


def clean_dataframe(df):
    # LIMPIAR CUSTOMER
    df["Cliente_ID"] = (
        df["Customer"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
    )

    # TRANSFORMAR PRODUCTOS
    productos = {
        "Product A": "Laptop",
        "Product B": "Smartphone",
        "Product C": "Tablet",
        "Product D": "Monitor",
        "Product E": "Teclado",
    }

    df["Producto"] = df["Product"].replace(productos)

    # TRANSFORMAR MESES
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
        "Dec": "Diciembre",
    }

    df["Mes"] = df["Month"].replace(meses)

    # RENOMBRAR COLUMNAS
    df = df.rename(columns={
        "Year": "Año",
        "Units_Sold": "Unidades_Vendidas",
        "Price_per_Unit": "Precio_Unitario",
        "Revenue": "Ingresos",
        "Customer_Name": "Nombre_Cliente",
    })

    # NORMALIZAR DECIMALES
    df["Precio_Unitario"] = df["Precio_Unitario"].round(2)
    df["Ingresos"] = df["Ingresos"].round(2)

    # ELIMINAR COLUMNAS ANTIGUAS
    df = df.drop(
        columns=["Customer", "Product", "Month"],
        errors="ignore"
    )

    return df


def extraer_y_limpiar(csv_path):
    df = extract_csv(csv_path)
    df = clean_dataframe(df)
    return df


print(">>> etl_ventas.py cargado")