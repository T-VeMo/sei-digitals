import streamlit as st

st.set_page_config(page_title="FL SEI SpA", page_icon="⚡", layout="wide", initial_sidebar_state="auto", menu_items={
        'Get Help': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Ñato scripts S.A."
    })

def pagina_principal():
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

pagina = st.navigation([
    st.Page(pagina_principal, title="Main", default=True),
    st.Page("pages/1_clientes.py", title="Clientes"),
    st.Page("pages/2_proveedores.py", title="Proveedores"),
    st.Page("pages/3_proyectos.py", title="Proyectos"),
    st.Page("pages/4_dashboard.py", title="Dashboard"),
    st.Page("pages/5_test_database.py", title="Test Database"),
])
pagina.run()

