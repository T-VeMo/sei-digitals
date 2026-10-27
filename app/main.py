import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st

st.set_page_config(page_title="FL SEI SpA", page_icon="⚡", layout="wide", initial_sidebar_state="auto", menu_items={
        'Get Help': 'https://www.youtube.com/watch?v=IWiosvGNRag',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Gecko Script"
    })

from core.auth.service import autenticar, crear_usuario

if "usuario" not in st.session_state:
    st.session_state.usuario = None

def pagina_login():
    col1, col2 = st.columns([1, 15])
    with col1:
        st.image("app/static/logo.png", width=80)
    with col2:
        st.title("SEI Digitals")
    st.subheader("Acceso al sistema")

    tab_ingresar, tab_crear = st.tabs(["Iniciar sesión", "Crear cuenta"])

    with tab_ingresar:
        with st.form("form_login"):
            correo = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar"):
                usuario, mensaje = autenticar(correo, password)
                if usuario:
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error(mensaje)

    with tab_crear:
        with st.form("form_registro"):
            nombre = st.text_input("Nombre completo")
            correo_n = st.text_input("Correo electrónico", key="correo_nuevo")
            pass_n = st.text_input("Contraseña", type="password", key="pass_nueva", max_chars=72)
            pass_n2 = st.text_input("Repetir contraseña", type="password", key="pass_nueva2", max_chars=72)
            if st.form_submit_button("Crear Cuenta"):
                if pass_n != pass_n2:
                    st.error("Las contraseñas no coinciden.")
                else:
                    ok, mensaje = crear_usuario(nombre, correo_n, pass_n)
                    (st.success if ok else st.error)(mensaje)

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


def cerrar_sesion():
    st.session_state.usuario = None
    st.rerun()

usuario = st.session_state.usuario

if usuario is None:
    pagina = st.navigation([st.Page(pagina_login, title="Ingresar", default=True)])
else:
    paginas = [
    st.Page(pagina_principal, title="Main", default=True),
    st.Page("pages/1_clientes.py", title="Clientes"),
    st.Page("pages/2_proveedores.py", title="Proveedores"),
    st.Page("pages/3_proyectos.py", title="Proyectos"),
    st.Page("pages/4_dashboard.py", title="Dashboard"),
    ]
    if usuario["rol"] == "admin":
        paginas.append(st.Page("pages/5_test_database.py", title="Test Database"))

    st.sidebar.write(f"👤 {usuario['nombre']} ({usuario['rol']})")
    if st.sidebar.button("Cerrar sesión"):
        cerrar_sesion()
    pagina = st.navigation(paginas)
pagina.run()

