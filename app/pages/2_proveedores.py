import streamlit as st 

st.title("📦 Gestión de Proveedores")
st.sidebar.image("app/static/logo.png", width=100)

if "proveedores" not in st.session_state:
    st.session_state.proveedores = [
        {"nombre": "Proveedor A", "email": "contacto@proveedorA.cl", "telefono": "+56 9 1111 2222", "categoria": "Eléctrico"},
        {"nombre": "Proveedor B", "email": "contacto@proveedorB.cl", "telefono": "+56 9 3333 4444", "categoria": "Plomería"},
    ]

@st.dialog("Correo inválido")
def mostrar_error_correo():
    st.warning("Es necesario agregar el @ en el correo electrónico.")

st.subheader("Registrar nuevo proveedor")

with st.form("form_nuevo_proveedor", clear_on_submit=True):
    nombre = st.text_input("Nombre del proveedor") 
    email = st.text_input("Email del proveedor")
    telefono = st.number_input("Teléfono del proveedor", min_value=0, step=1, format="%d")
    categoria = st.text_input("Categoría del proveedor")

    enviado = st.form_submit_button("Registrar proveedor")

    if enviado:
        if nombre and email and telefono > 0 and categoria:
            if "@" in email:
                st.session_state.proveedores.append({"nombre": nombre, "email": email, "telefono": str(telefono), "categoria": categoria})
                st.success(f"Proveedor {nombre} registrado exitosamente.")
            else:
                mostrar_error_correo()
        else:
            st.error("Por favor, complete todos los campos obligatorios.")

st.divider()
st.subheader("Proveedores registrados")

if len(st.session_state.proveedores) == 0:
    st.info("Aún no hay proveedores registrados")
else:
    for i, proveedor in enumerate(st.session_state.proveedores):
        col1, col2, col3, col4, col5 = st.columns([3, 4, 3, 2, 1])
        with col1:
            st.write(proveedor["nombre"])
        with col2:
            st.write(proveedor["email"])
        with col3:
            st.write(proveedor["telefono"])
        with col4:
            st.write(proveedor["categoria"])
        with col5:
            if st.button("❌", key=f"eliminar_{i}"):
                st.session_state.proveedores.pop(i)
                st.rerun() 