import streamlit as st

st.title("👥 Gestión de Clientes")
st.sidebar.image("app/static/logo.png", width=100)

#ESTO GUARDA LA INFORMACIÓN DE LOS CLIENTES EN LA SESIÓN
if "clientes" not in st.session_state:
    st.session_state.clientes = [
        {"nombre": "Constructora Andes SpA", "email": "contacto@andes.cl", "telefono": "+56 9 1234 5678"},
        {"nombre": "Inmobiliaria Costa Azul", "email": "contacto@costaazul.cl", "telefono": "+56 9 8765 4321"},
    ]

@st.dialog("Correo inválido")
def mostrar_error_correo():
    st.warning("Es necesario agregar el @ en el correo electrónico.")

st.subheader("Registrar nuevo cliente")
#FORMULARIO PARA REGISTRAR NUEVO CLIENTE
with st.form("form_nuevo_cliente", clear_on_submit=True):
    nombre = st.text_input("Nombre del cliente")
    email = st.text_input("Correo electrónico")
    telefono = st.number_input("Teléfono", min_value=0, step=1, format="%d")

    enviado= st.form_submit_button("Registrar cliente")

    if enviado:
        if nombre and email and telefono > 0:
            if "@" in email:
                st.session_state.clientes.append({"nombre": nombre, "email": email, "telefono": str(telefono)})
                st.success(f"Cliente {nombre} registrado exitosamente.")
            else:
                mostrar_error_correo()
        else:
            st.error("Por favor, complete todos los campos obligatorios.")

st.divider()
st.subheader("Clientes registrados")

if len(st.session_state.clientes) == 0:
    st.info("Aún no hay clientes nuevos")
else:
    for i, cliente in enumerate(st.session_state.clientes):
        col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
        with col1:
            st.write(cliente["nombre"])
        with col2:
            st.write(cliente["email"])  
        with col3:
            st.write(cliente["telefono"])
        with col4:
            if st.button("❌", key=f"eliminar_{i}"):
                st.session_state.clientes.pop(i)
                st.rerun()