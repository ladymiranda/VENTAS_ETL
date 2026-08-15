from pydantic import BaseModel, ValidationError


class Venta(BaseModel):

    Año: int
    Mes: str
    Cliente_ID: int
    Producto: str
    Unidades_Vendidas: int
    Precio_Unitario: float
    Ingresos: float
    Nombre_Cliente: str


def validate_dataframe(df):

    errores = []

    for i, row in enumerate(df.to_dicts(), start=1):

        try:
            Venta(**row)

        except ValidationError as e:

            errores.append(
                {
                    "fila": i,
                    "error": e.errors()
                }
            )

    return errores