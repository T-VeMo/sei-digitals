import streamlit as st
from utils import formato_clp

st.title("Proyectos")
st.sidebar.image("app/static/logo.png", width=100)

if "proyectos" not in st.session_state:
    st.session_state.proyectos = [
        {"nombre": "Instalacion colegio", 
         "cliente": "Juan Pérez", 
         "fecha_inicio": "01/01/2027", 
         "fecha_termino": "01/01/2028", 
         "costo_insumos": 1000000, 
         "costo_mano_obra": 2000000, 
         "estado": "En progreso"},
        ]

st.subheader("Registro de proyectos")

with st.form("form_nuevo_proyecto", clear_on_submit=True):
    nombre_proyecto = st.text_input("Nombre del proyecto")
    cliente_asociado = st.text_input("Cliente asociado")
    fecha_inicio = st.date_input("Fecha de inicio")
    fecha_termino = st.date_input("Fecha estimada de término")
    costo_insumos = st.number_input("Costo de insumos", min_value=0)
    costo_mano_obra = st.number_input("Costo de mano de obra", min_value=0)
    estado_proyecto = st.selectbox("Estado del proyecto", ["En progreso", "Finalizado", "Cancelado"])

    enviado = st.form_submit_button("Registrar proyecto")

    if enviado:
        if nombre_proyecto and cliente_asociado and fecha_inicio and fecha_termino and costo_insumos >= 0 and costo_mano_obra >= 0 and estado_proyecto:
            st.session_state.proyectos.append({
                "nombre": nombre_proyecto,
                "cliente": cliente_asociado,
                "fecha_inicio": fecha_inicio.strftime("%d/%m/%Y"),
                "fecha_termino": fecha_termino.strftime("%d/%m/%Y"),
                "costo_insumos": costo_insumos,
                "costo_mano_obra": costo_mano_obra,
                "estado": estado_proyecto
            })
            st.success(f"Proyecto {nombre_proyecto} registrado exitosamente.")
        else:
            st.error("Por favor, complete todos los campos obligatorios.")

st.divider()
st.subheader("Proyectos registrados")

if len(st.session_state.proyectos) == 0:
    st.info("Aún no hay proyectos registrados")
else:
    for i, proyecto in enumerate(st.session_state.proyectos):
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([4, 3, 3, 3, 3, 3, 3, 1])
        with col1:
            st.write(proyecto["nombre"])
        with col2:
            st.write(proyecto["cliente"])
        with col3:
            st.write(proyecto["fecha_inicio"])
        with col4:
            st.write(proyecto["fecha_termino"])
        with col5:
            st.write(formato_clp(proyecto["costo_insumos"]))
        with col6:
            st.write(formato_clp(proyecto["costo_mano_obra"]))
        with col7:
            st.write(proyecto["estado"])
        with col8:
            if st.button("❌", key=f"eliminar_{i}"):
                st.session_state.proyectos.pop(i)
                st.rerun()