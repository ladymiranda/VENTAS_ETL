import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

from src.utils.config import DB_PATH


# ==========================
# CONFIGURACION
# ==========================

st.set_page_config(
    page_title="Dashboard Ventas",
    page_icon="📊",
    layout="wide"
)


# ==========================
# CONEXION DUCKDB
# ==========================

conn = duckdb.connect(DB_PATH)


df = conn.execute(
    "SELECT * FROM ventas_raw"
).df()


conn.close()


# ==========================
# TITULO
# ==========================

st.title("📊 Dashboard de Ventas")
st.write("Análisis interactivo de ventas")


# ==========================
# FILTROS
# ==========================

st.sidebar.header("🔎 Filtros")


filtro_anio = st.sidebar.multiselect(
    "Año",
    options=sorted(df["Año"].unique())
)


filtro_producto = st.sidebar.multiselect(
    "Producto",
    options=sorted(df["Producto"].unique())
)


filtro_mes = st.sidebar.multiselect(
    "Mes",
    options=[
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"
    ]
)



# ==========================
# APLICAR FILTROS
# ==========================

df_filter = df.copy()


if filtro_anio:
    df_filter = df_filter[
        df_filter["Año"].isin(filtro_anio)
    ]


if filtro_producto:
    df_filter = df_filter[
        df_filter["Producto"].isin(filtro_producto)
    ]


if filtro_mes:
    df_filter = df_filter[
        df_filter["Mes"].isin(filtro_mes)
    ]



# ==========================
# VALIDAR DATA
# ==========================

if df_filter.empty:

    st.warning(
        "⚠️ No existen datos para los filtros seleccionados"
    )

    st.stop()



# ==========================
# KPIS
# ==========================

ingresos_total = df_filter["Ingresos"].sum()

unidades_total = df_filter["Unidades_Vendidas"].sum()

clientes_total = df_filter["Cliente_ID"].nunique()



col1, col2, col3 = st.columns(3)


col1.metric(
    "💰 Ingresos Totales",
    f"$ {ingresos_total:,.2f}"
)


col2.metric(
    "📦 Unidades Vendidas",
    f"{unidades_total:,}"
)


col3.metric(
    "👥 Clientes",
    clientes_total
)



st.divider()



# ==========================
# INGRESOS POR PRODUCTO
# ==========================

st.subheader("📈 Ingresos por Producto")


ventas_producto = (
    df_filter
    .groupby("Producto")["Ingresos"]
    .sum()
    .reset_index()
)


fig_producto = px.bar(
    ventas_producto,
    x="Producto",
    y="Ingresos",
    text_auto=".2s",
    title="Ingresos por Producto"
)


st.plotly_chart(
    fig_producto,
    use_container_width=True
)



# ==========================
# EVOLUCION MENSUAL
# ==========================

st.subheader("📅 Evolución Mensual")


orden_mes = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre"
]


ventas_mes = (
    df_filter
    .groupby("Mes")["Ingresos"]
    .sum()
    .reset_index()
)


ventas_mes["Mes"] = pd.Categorical(
    ventas_mes["Mes"],
    categories=orden_mes,
    ordered=True
)


ventas_mes = ventas_mes.sort_values(
    "Mes"
)



fig_mes = px.line(
    ventas_mes,
    x="Mes",
    y="Ingresos",
    markers=True,
    title="Tendencia de Ingresos por Mes"
)


st.plotly_chart(
    fig_mes,
    use_container_width=True
)



# ==========================
# TOP CLIENTES
# ==========================

st.subheader("🏆 Top 10 Clientes")


top_clientes = (
    df_filter
    .groupby("Nombre_Cliente")["Ingresos"]
    .sum()
    .reset_index()
    .sort_values(
        "Ingresos",
        ascending=False
    )
    .head(10)
)



fig_clientes = px.bar(
    top_clientes,
    x="Nombre_Cliente",
    y="Ingresos",
    title="Clientes con mayores ingresos"
)


st.plotly_chart(
    fig_clientes,
    use_container_width=True
)



# ==========================
# TABLA DETALLE
# ==========================

st.subheader("📄 Detalle de Ventas")


st.dataframe(
    df_filter,
    use_container_width=True
)