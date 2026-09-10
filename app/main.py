import streamlit as st

st.set_page_config(page_title="FL SEI SpA", page_icon="⚡", layout="wide", initial_sidebar_state="auto", menu_items={
        'Get Help': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Ñato scripts S.A."
    })

st.sidebar.image("app/static/logo.png", width=100)

col1, col2 = st.columns([1, 15])

with col1:
    st.image("app/static/logo.png", width=80)

with col2:
    st.title("SEI Digitals")

st.subheader("Sistema de gestión integral — FL Servicios Eléctricos Integrales SpA")
st.write("""
Bienvenido al sistema de gestión de SEI Digitals. 
Usa el menú de la barra lateral para navegar entre los módulos: 
Clientes, Proveedores, Dashboards y más.
""")
st.caption("Proyecto APT — Ingeniería Informática, Duoc UC | Moisés Roa · Tomás Vega · Natanael Yáñez")
