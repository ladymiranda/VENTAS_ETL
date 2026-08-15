"""
modulos/schema.py

Esquema esperado del dataset de ventas ya transformado (Pandera).
Separado de validacion.py para que el esquema se pueda importar solo 
sin arrastrar la lógica de validación.
"""

from pandera.pandas import Column, Check, DataFrameSchema


MESES_VALIDOS = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


schema_ventas = DataFrameSchema(
    columns={
        "Año":                 Column(int, Check.in_range(2000, 2100)),
        "Mes":                 Column(str, Check.isin(MESES_VALIDOS)),
        "Cliente_ID":          Column(int, Check.greater_than(0)),
        "Producto":            Column(str, nullable=False),
        "Unidades_Vendidas":   Column(int, Check.greater_than(0)),
        "Precio_Unitario":     Column(float, Check.greater_than(0)),
        "Ingresos":            Column(float, Check.greater_than_or_equal_to(0)),
        "Nombre_Cliente":      Column(str, nullable=False),
    },
    checks=Check(
        lambda df: (df["Ingresos"] - df["Unidades_Vendidas"] * df["Precio_Unitario"]).abs() < 0.5,
        error="Ingresos no coincide con Unidades_Vendidas * Precio_Unitario"
    ),
    coerce=True,
)
