import streamlit as st
import pandas as pd
import plotly.express as px
from utils import formato_clp

from core.dashboard.queries import (
    obtener_kpis, ventas_por_cliente, compras_por_proveedor, facturas_por_estado
)


st.title("📊Dashboard")
st.sidebar.image("app/static/logo.png", width=100)

# ============================================
# FILA 1 — TARJETAS KPI
# ============================================
kpis = obtener_kpis()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingresos totales", formato_clp(kpis["ingresos"]))
col2.metric("Ganancia neta", formato_clp(kpis["ganancia"]))
col3.metric("Total de compras", formato_clp(kpis["costos"]))
col4.metric("Clientes registrados", kpis["clientes"])

st.divider()

# ============================================
# FILA 2 — TOP Clientes
# ============================================

st.subheader("Clientes con mas ventas")

df_clientes = ventas_por_cliente()
if df_clientes.empty:
    st.info("Aún no hay ventas registradas.")
else:
    fig_clientes = px.bar(df_clientes, x="cliente", y="ventas", title="Top clientes por ventas")
    st.plotly_chart(fig_clientes, use_container_width=True)

# ============================================
# FILA 3 — PROVEEDORES Y ESTADO DE FACTURAS
# ============================================
col5, col6 = st.columns(2)

with col5:
    st.subheader("Proveedores")
    df_proveedores = compras_por_proveedor()
    if df_proveedores.empty:
        st.info("Aún no hay compras registradas.")
    else:
        fig_proveedores = px.bar(df_proveedores, x="proveedor", y="transacciones",
                                 title="Proveedores más frecuentes")
        st.plotly_chart(fig_proveedores, use_container_width=True)

with col6:
    st.subheader("Facturas")
    df_estado = facturas_por_estado()
    if df_estado.empty:
        st.info("Aún no hay facturas registradas.")
    else:
        fig_facturas = px.pie(df_estado, names="estado", values="cantidad",
                              title="Facturas de venta: pagadas vs pendientes")
        st.plotly_chart(fig_facturas, use_container_width=True)