import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from config.config import DB_PATH


# ==========================
# CONSTANTES
# ==========================

ORDEN_MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

COLOR_PRINCIPAL = "#2a78d6"
COLOR_ESCALA = "Blues"


# ==========================
# CARGA Y PREPARACION DE DATOS (cacheadas)
# ==========================

@st.cache_data
def cargar_datos():
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    df = conn.execute("SELECT * FROM ventas_raw").df()
    conn.close()
    return df


@st.cache_data
def preparar_datos(df):
    df = df.copy()
    df["Mes"] = pd.Categorical(df["Mes"], categories=ORDEN_MESES, ordered=True)
    df["Ticket_Promedio"] = (df["Ingresos"] / df["Unidades_Vendidas"]).round(2)
    return df


# ==========================
# CONFIGURACION DE PAGINA
# ==========================

def configurar_pagina():
    st.set_page_config(
        page_title="Dashboard Ventas",
        page_icon="📊",
        layout="wide",
    )
    st.title("📊 Dashboard de Ventas")
    st.write("Análisis interactivo de ventas")


# ==========================
# FILTROS (sidebar)
# ==========================

def sidebar_filtros(df):
    st.sidebar.header("🔎 Filtros")

    filtro_anio = st.sidebar.multiselect("Año", options=sorted(df["Año"].unique()))
    filtro_producto = st.sidebar.multiselect("Producto", options=sorted(df["Producto"].unique()))
    filtro_mes = st.sidebar.multiselect("Mes", options=ORDEN_MESES)

    df_filtrado = df.copy()

    if filtro_anio:
        df_filtrado = df_filtrado[df_filtrado["Año"].isin(filtro_anio)]

    if filtro_producto:
        df_filtrado = df_filtrado[df_filtrado["Producto"].isin(filtro_producto)]

    if filtro_mes:
        df_filtrado = df_filtrado[df_filtrado["Mes"].isin(filtro_mes)]

    if df_filtrado.empty:
        st.warning("⚠️ No existen datos para los filtros seleccionados")
        st.stop()

    return df_filtrado


# ==========================
# TAB 1 — RESUMEN GENERAL
# ==========================

def tab_resumen_general(df):
    ingresos_total = df["Ingresos"].sum()
    unidades_total = df["Unidades_Vendidas"].sum()
    clientes_total = df["Cliente_ID"].nunique()
    ticket_promedio = ingresos_total / unidades_total if unidades_total else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Ingresos Totales", f"$ {ingresos_total:,.2f}")
    col2.metric("📦 Unidades Vendidas", f"{unidades_total:,}")
    col3.metric("👥 Clientes", clientes_total)
    col4.metric("🎟️ Ticket Promedio", f"$ {ticket_promedio:,.2f}")

    st.divider()

    st.subheader("📈 Ingresos por Producto")
    ventas_producto = df.groupby("Producto")["Ingresos"].sum().reset_index()
    fig_producto = px.bar(
        ventas_producto, x="Producto", y="Ingresos", text_auto=".2s",
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    st.plotly_chart(fig_producto, use_container_width=True)

    st.subheader("📅 Evolución Mensual")
    ventas_mes = (
        df.groupby("Mes", observed=True)["Ingresos"]
        .sum()
        .reset_index()
        .sort_values("Mes")
    )
    fig_mes = px.line(
        ventas_mes, x="Mes", y="Ingresos", markers=True,
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    st.plotly_chart(fig_mes, use_container_width=True)


# ==========================
# TAB 2 — ANALISIS COMPARATIVO
# ==========================

def tab_analisis_comparativo(df):
    st.subheader("🔬 Precio Unitario vs Unidades Vendidas")
    fig_scatter = px.scatter(
        df, x="Precio_Unitario", y="Unidades_Vendidas", color="Producto",
        hover_data=["Nombre_Cliente"],
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("📦 Distribución de Ingresos por Producto")
    fig_box = px.box(df, x="Producto", y="Ingresos", color="Producto")
    st.plotly_chart(fig_box, use_container_width=True)


# ==========================
# TAB 3 — EXPLORADOR
# ==========================

def tab_explorador(df):
    st.subheader("📄 Explorador de Ventas")
    st.dataframe(df, use_container_width=True)

    st.subheader("🔍 Ficha de Cliente")
    cliente_sel = st.selectbox("Selecciona un cliente", sorted(df["Nombre_Cliente"].unique()))

    ficha = df[df["Nombre_Cliente"] == cliente_sel]

    col1, col2, col3 = st.columns(3)
    col1.metric("Compras", len(ficha))
    col2.metric("Ingresos generados", f"$ {ficha['Ingresos'].sum():,.2f}")
    col3.metric("Ticket promedio", f"$ {ficha['Ingresos'].mean():,.2f}")

    st.dataframe(ficha, use_container_width=True)


# ==========================
# TAB 4 — CORRELACIONES
# ==========================

def tab_correlaciones(df):
    st.subheader("🌡️ Correlación entre variables numéricas")
    columnas_numericas = ["Unidades_Vendidas", "Precio_Unitario", "Ingresos"]
    corr = df[columnas_numericas].corr()

    fig_heatmap = px.imshow(
        corr, text_auto=".2f", color_continuous_scale=COLOR_ESCALA, aspect="auto",
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.subheader("🏆 Top 10 Clientes")
    top_clientes = (
        df.groupby("Nombre_Cliente")["Ingresos"]
        .sum()
        .reset_index()
        .sort_values("Ingresos", ascending=False)
        .head(10)
    )
    fig_clientes = px.bar(
        top_clientes, x="Nombre_Cliente", y="Ingresos",
        color_discrete_sequence=[COLOR_PRINCIPAL],
    )
    st.plotly_chart(fig_clientes, use_container_width=True)


# ==========================
# MAIN
# ==========================

def main():
    configurar_pagina()

    df_raw = cargar_datos()
    df = preparar_datos(df_raw)

    df_filtrado = sidebar_filtros(df)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Resumen General",
        "🔬 Análisis Comparativo",
        "🔎 Explorador",
        "🌡️ Correlaciones",
    ])

    with tab1:
        tab_resumen_general(df_filtrado)

    with tab2:
        tab_analisis_comparativo(df_filtrado)

    with tab3:
        tab_explorador(df_filtrado)

    with tab4:
        tab_correlaciones(df_filtrado)


if __name__ == "__main__":
    main()
