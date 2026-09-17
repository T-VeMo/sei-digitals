import streamlit as st
import pandas as pd
import plotly.express as px
from utils import formato_clp

st.title("📊Dashboard")
st.sidebar.image("app/static/logo.png", width=100)

# ============================================
# DATOS DE PRUEBA — reemplazar cuando existan los módulos reales
# ============================================

# TODO: reemplazar por datos reales de ventas cuando exista compras_ventas_facturacion.py
ingresos_totales = 45000000
costos_totales = sum(p["costo_insumos"] + p["costo_mano_obra"] for p in st.session_state.get("proyectos", []))
ganancia_neta = ingresos_totales - costos_totales

# TODO: reemplazar por conteo real de clientes registrados este mes
nuevos_clientes_mes = 3

# TODO: reemplazar por consulta real (suma de ventas por cliente)
clientes_top_ventas = pd.DataFrame([
    {"cliente": "Constructora Andes SpA", "ventas": 12000000},
    {"cliente": "Inmobiliaria Costa Azul", "ventas": 9500000},
    {"cliente": "Juan Pérez", "ventas": 7200000},
])

# TODO: reemplazar por conteo real de transacciones por proveedor
proveedores_frecuentes = pd.DataFrame([
    {"proveedor": "Proveedor A", "transacciones": 14},
    {"proveedor": "Proveedor B", "transacciones": 9},
])

# TODO: reemplazar por conteo real de facturas pagadas/impagas
facturas_estado = pd.DataFrame([
    {"estado": "Pagadas", "cantidad": 22},
    {"estado": "Impagas", "cantidad": 5},
])

# ============================================
# FILA 1 — TARJETAS KPI
# ============================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Ganancia neta",
        value=formato_clp(ganancia_neta),
        delta=formato_clp(ganancia_neta - 3000000)  # comparado con un valor de referencia de prueba
    )

with col2:
    st.metric(label="Nuevos clientes (mes)", value=nuevos_clientes_mes, delta=1)

with col3:
    st.metric(label="Total invertido en proyectos", value=formato_clp(costos_totales))

st.divider()

# ============================================
# FILA 2 — PRECIO DE INSUMO VARIABLE (ejemplo)
# ============================================

st.subheader("Insumos con precio variable")

col4, col5 = st.columns(2)

with col4:
    st.metric(label="Cable eléctrico (por metro)", value=formato_clp(15000), delta=formato_clp(1500))

with col5:
    st.metric(label="Cobre (por kg)", value=formato_clp(8200), delta=formato_clp(-300))

st.divider()

# ============================================
# FILA 3 — GRÁFICOS DE PROYECTOS (datos reales, ya existentes)
# ============================================

st.subheader("Costos por proyecto")

if len(st.session_state.get("proyectos", [])) > 0:
    df_proyectos = pd.DataFrame(st.session_state.proyectos)
    df_proyectos["costo_total"] = df_proyectos["costo_insumos"] + df_proyectos["costo_mano_obra"]

    col6, col7 = st.columns(2)

    with col6:
        fig_barras = px.bar(df_proyectos, x="nombre", y="costo_total", title="Costo total por proyecto")
        st.plotly_chart(fig_barras)

    with col7:
        fig_torta = px.pie(df_proyectos, names="estado", title="Proyectos por estado")
        st.plotly_chart(fig_torta)
else:
    st.info("Aún no hay proyectos registrados para graficar.")

st.divider()

# ============================================
# FILA 4 — GRÁFICOS CON DATOS DE PRUEBA (ventas, proveedores, facturas)
# ============================================

st.subheader("Clientes con más ventas")
fig_clientes = px.bar(clientes_top_ventas, x="cliente", y="ventas", title="Top clientes por ventas")
st.plotly_chart(fig_clientes)

col8, col9 = st.columns(2)

with col8:
    fig_proveedores = px.bar(proveedores_frecuentes, x="proveedor", y="transacciones", title="Proveedores más frecuentes")
    st.plotly_chart(fig_proveedores)

with col9:
    fig_facturas = px.pie(facturas_estado, names="estado", values="cantidad", title="Facturas: pagadas vs impagas")
    st.plotly_chart(fig_facturas)