# VentasApp

Pipeline de datos de ventas (ETL con validación de esquema) + dashboard
interactivo en Streamlit.

```
CSV crudo -> extracción/limpieza -> validación (Pandera) -> feature engineering -> Parquet + DuckDB -> Dashboard (Streamlit)
```

## Contexto del proyecto

### Qué datos tiene

La fuente es un único CSV (`data/raw/Base de datos de Ventas.csv`) con
transacciones de venta de 5 productos electrónicos (Laptop, Smartphone,
Tablet, Monitor, Teclado) entre 2019 y 2023. Cada fila es una venta:
año, mes, cliente, producto, unidades vendidas, precio unitario e ingreso
generado. ~5,000 registros.

### Qué le hace el ETL a esos datos

**1. Extracción y transformación** (`modulos/etl_ventas.py`)
El CSV llega en inglés y con el cliente mezclado en un solo texto
(`"Customer 103"`). Este paso:
- separa el número de cliente a una columna propia (`Cliente_ID`, entero),
- traduce los nombres de producto y los meses al español,
- renombra todas las columnas a español (`Year` → `Año`,
  `Units_Sold` → `Unidades_Vendidas`, `Revenue` → `Ingresos`, etc.),
- redondea precios e ingresos a 2 decimales.

**2. Validación** (`modulos/schema.py` + `modulos/validacion.py`)
Antes de confiar en los datos, Pandera los revisa contra las reglas de
negocio de la tabla de más abajo (por ejemplo: `Ingresos` debe coincidir
con `Unidades_Vendidas * Precio_Unitario`, no puede haber unidades o
precios negativos, el mes tiene que ser uno de los 12 válidos). Las filas
que fallan se descartan y quedan registradas en el log — el pipeline no
se detiene por un puñado de filas corruptas, pero tampoco deja pasar datos
que romperían las cuentas del dashboard.

**3. Feature engineering** (`modulos/feature_engineering.py`)
Sobre los datos ya validados, se agregan columnas derivadas que no vienen
en el CSV original: historial de compras por cliente (`total_compras`,
`monto_total`, `ticket_promedio`, `monto_max`), hace cuántos meses compró
por última vez cada cliente (`meses_desde_ultima_compra`), qué tan grande
es la participación de cada producto en el revenue total
(`participacion_pct`, `ranking_producto`), y en qué segmento de valor cae
cada cliente por cuartiles (`segmento_valor`: Bajo/Medio-bajo/Medio-alto/Alto).

**4. Load** (`etl_ventas_main.py`)
El dataset final (limpio + validado + enriquecido, ~20 columnas) se guarda
en dos formatos en `output/`: `ventas.parquet` (columnar, portable) y
`ventas.duckdb` (tabla `ventas_raw`, consultable por SQL) — este segundo
es el que lee el dashboard.

### Para qué sirve / qué se analiza en el dashboard (`dashboard.py`)

El dashboard responde preguntas de negocio sobre estos datos, con filtros
por año, producto y mes:

- **Resumen General** — salud del negocio de un vistazo: ingresos totales,
  unidades vendidas, número de clientes, ticket promedio; qué producto
  genera más ingresos; cómo evolucionan los ingresos mes a mes.
- **Análisis Comparativo** — si el precio unitario se relaciona con el
  volumen vendido, y qué tan dispersos son los ingresos dentro de cada
  producto (outliers, consistencia de precios).
- **Explorador** — la tabla completa filtrable, más una ficha por cliente
  individual (cuánto compró, cuánto generó, su ticket promedio).
- **Correlaciones** — qué tan relacionadas están unidades, precio e
  ingresos entre sí, y quiénes son los 10 clientes que más ingresos
  generan (para priorizar en campañas de retención, por ejemplo).

`Pruebas.ipynb` es el espacio para explorar preguntas nuevas antes de
llevarlas al dashboard — importa los mismos módulos de producción, así que
lo que se valida ahí es exactamente el código que corre en `etl_ventas_main.py`.

## Estructura del proyecto

```
VentasApp/
├── config/
│   └── config.py            # Rutas del proyecto y variables de entorno (.env)
├── data/
│   └── raw/                 # CSV de ventas original (fuente cruda, no se modifica)
├── logs/                    # Logs del ETL (etl.log, no versionado)
├── modulos/
│   ├── etl_ventas.py            # Extracción del CSV + limpieza/renombrado de columnas
│   ├── schema.py                 # Esquema esperado del dataset (Pandera DataFrameSchema)
│   ├── validacion.py             # Valida el DataFrame contra schema.py
│   └── feature_engineering.py    # Historial de cliente, recencia, ranking de producto, segmentación
├── output/
│   ├── ventas.parquet       # Dataset limpio y enriquecido (formato columnar)
│   └── ventas.duckdb        # Mismo dataset, consultable por SQL (lo lee el dashboard)
├── utils/
│   └── logging_utils.py     # Configuración de logging (consola + archivo)
├── etl_ventas_main.py       # Orquestador: corre todo el pipeline de punta a punta
├── dashboard.py             # App de Streamlit (lee de output/ventas.duckdb)
├── Pruebas.ipynb            # Notebook de exploración/prototipado
├── requirements.txt
├── .env.example             # Plantilla de variables de entorno (copiar a .env)
└── .gitignore
```

> **Nota:** `_to_delete/` contiene el código de la estructura anterior
> (`src/`, `main.py` viejo). Bórrala una vez que confirmes que todo lo demás
> funciona — no se elimina automáticamente por seguridad.

## Requisitos

- Python 3.11+
- Ver `requirements.txt` para las dependencias exactas.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

copy .env.example .env        # Windows (o "cp" en macOS/Linux)
```

`.env` no se sube a git (está en `.gitignore`). Hoy el proyecto no usa
API keys ni credenciales externas — DuckDB es un archivo local — pero
`.env` ya deja el patrón listo para cuando se agregue algo sensible.

Variables actuales en `.env`:

| Variable | Para qué sirve | Default |
|---|---|---|
| `APP_ENV` | Etiqueta informativa del entorno (development/production) | `development` |
| `LOG_LEVEL` | Nivel de detalle del logging (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `STREAMLIT_SERVER_PORT` | Puerto local al correr el dashboard (Streamlit Cloud lo ignora) | `8501` |

## Cómo correr el ETL

Extrae el CSV, valida el esquema con Pandera, genera las features derivadas
y guarda el resultado en `output/`:

```bash
python etl_ventas_main.py
```

Si Pandera encuentra registros que no cumplen el esquema (`modulos/schema.py`),
los elimina del dataset y lo indica en el log (`logs/etl.log`) — el proceso
no se detiene, sigue con los registros válidos.

## Cómo correr el dashboard

```bash
streamlit run dashboard.py
```

Se abre en `http://localhost:8501` (o el puerto que definas en `.env`).

## Despliegue en Streamlit Community Cloud

1. Sube los cambios a GitHub (incluyendo `output/ventas.parquet` y
   `output/ventas.duckdb` — el deploy en la nube no corre `etl_ventas_main.py`,
   así que el dashboard necesita esos archivos ya generados en el repo).
2. En [share.streamlit.io](https://share.streamlit.io), **Create app** →
   selecciona el repo, rama `main`, archivo principal `dashboard.py`.
3. Si necesitas variables de entorno en la nube, se configuran en
   **Advanced settings → Secrets** (no lee `.env` directamente).

## Esquema de datos (`modulos/schema.py`)

| Columna | Tipo | Regla |
|---|---|---|
| `Año` | int | entre 2000 y 2100 |
| `Mes` | str | uno de los 12 meses en español |
| `Cliente_ID` | int | mayor a 0 |
| `Producto` | str | no nulo |
| `Unidades_Vendidas` | int | mayor a 0 |
| `Precio_Unitario` | float | mayor a 0 |
| `Ingresos` | float | mayor o igual a 0, y debe coincidir con `Unidades_Vendidas * Precio_Unitario` |
| `Nombre_Cliente` | str | no nulo |
